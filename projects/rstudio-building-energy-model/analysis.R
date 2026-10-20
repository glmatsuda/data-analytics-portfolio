stopifnot(unname(tools::md5sum("data/source.csv")) == trimws(readLines("data/source.md5")))
# Run from the project root: source("analysis.R") or Rscript --vanilla analysis.R
# Base/recommended R only; the provided data is an attributed public snapshot.
dir.create("results", showWarnings = FALSE)
x <- read.csv("data/source.csv", check.names = FALSE, colClasses = "character", na.strings = c("", "NA", "N/A"))
num <- function(v) suppressWarnings(as.numeric(gsub(",", "", v, fixed = TRUE)))
x$id <- x$OSEBuildingID; x$year <- num(x$DataYear)
x$eui <- num(x[["SiteEUIWN(kBtu/sf)"]]); x$area <- num(x$SelfReportGFATotal); x$built <- num(x$YearBuilt)
stopifnot(!anyDuplicated(paste(x$id,x$year)))
eligible <- x$ComplianceStatus == "Compliant" & x$Demolished == "false" & is.finite(x$eui) & x$eui > 0
x$eligible <- eligible
# Predictors are strictly the previous reporting year's values.
previous <- data.frame(id=x$id,target_year=x$year+1,previous_year=x$year,previous_eui=x$eui,previous_area=x$area,
  previous_age=x$year-x$built,previous_type=x$EPAPropertyType,previous_eligible=x$eligible,stringsAsFactors=FALSE)
target <- data.frame(id=x$id,target_year=x$year,actual=x$eui,target_eligible=x$eligible)
paired <- merge(previous,target,by=c("id","target_year"))
ok <- with(paired,previous_eligible & target_eligible & is.finite(previous_area) & previous_area>0 & is.finite(previous_age) & previous_age>=0 & previous_age<=250 & !is.na(previous_type))
paired <- paired[which(ok),]; paired <- paired[order(paired$target_year,paired$id),]
write.csv(data.frame(stage=c("source rows","eligible source rows","matched property-year transitions","model-eligible transitions"),
  rows=c(nrow(x),sum(eligible,na.rm=TRUE),nrow(merge(previous,target,by=c("id","target_year"))),nrow(paired))),"results/row-flow.csv",row.names=FALSE)
train <- subset(paired,target_year<=2023); test <- subset(paired,target_year==2024)
stopifnot(nrow(train)>100,nrow(test)>100,max(train$target_year)<min(test$target_year),all(paired$previous_year==paired$target_year-1))
fit_model <- function(d) {
  counts <- table(d$previous_type); common <- names(counts[counts>=50]); groups <- unique(c(common,"Other"))
  d$use_group <- factor(ifelse(d$previous_type %in% common,d$previous_type,"Other"),levels=groups)
  fit <- lm(log1p(actual) ~ log1p(previous_eui)+log(previous_area)+previous_age+use_group,data=d)
  list(fit=fit,common=common,levels=groups,smearing=mean(exp(residuals(fit))))
}
forecast <- function(bundle,d) {
  d$use_group <- factor(ifelse(d$previous_type %in% bundle$common,d$previous_type,"Other"),levels=bundle$levels)
  pmax(0,exp(predict(bundle$fit,newdata=d))*bundle$smearing-1)
}
score <- function(actual,prediction,label,population) data.frame(population=population,model=label,n=length(actual),MAE=mean(abs(actual-prediction)),RMSE=sqrt(mean((actual-prediction)^2)),RMSLE=sqrt(mean((log1p(actual)-log1p(prediction))^2)))
# Temporal development check: never tune against the final 2024 holdout.
dev <- subset(train,target_year<=2022); validation <- subset(train,target_year==2023)
validation_bundle <- fit_model(dev); bundle <- fit_model(train)
test$model_prediction <- forecast(bundle,test);test$baseline_prediction <- test$previous_eui
metrics <- rbind(score(validation$actual,forecast(validation_bundle,validation),"Log-linear lag model","2023 validation"),
  score(validation$actual,validation$previous_eui,"Previous-year EUI","2023 validation"),
  score(test$actual,test$model_prediction,"Log-linear lag model","2024 holdout"),score(test$actual,test$baseline_prediction,"Previous-year EUI","2024 holdout"))
write.csv(metrics,"results/metrics.csv",row.names=FALSE)
write.csv(test[,c("id","previous_year","target_year","previous_type","actual","previous_eui","model_prediction","baseline_prediction")],"results/predictions.csv",row.names=FALSE)
write.csv(data.frame(term=names(coef(bundle$fit)),estimate=unname(coef(bundle$fit))),"results/coefficients.csv",row.names=FALSE)
write.csv(data.frame(split=c("train","validation","holdout"),target_start=c(min(train$target_year),2023,2024),target_end=c(2023,2023,2024),n=c(nrow(train),nrow(validation),nrow(test))),"results/split-audit.csv",row.names=FALSE)
saveRDS(bundle,"results/energy-model.rds");saveRDS(list(train=train,test=test,metrics=metrics),"results/validation-state.rds")
capture.output(sessionInfo(),file="results/session-info.txt")
png("results/model-diagnostics.png",width=1600,height=1000,res=130,type=if (Sys.info()[["sysname"]]=="Darwin") "quartz" else "cairo")
par(oma=c(0,0,3,0),mfrow=c(1,2),mar=c(5,5,4,2),bg="#F3F6F8",col.axis="#526978",col.lab="#172C3C",col.main="#172C3C")
plot(log1p(test$actual),log1p(test$model_prediction),pch=16,col=adjustcolor("#137E8D",alpha.f=.32),xlab="Observed log(1 + EUI)",ylab="Predicted log(1 + EUI)",main="2024 holdout: observed vs predicted");abline(0,1,col="#B46510",lwd=2)
hold <- subset(metrics,population=="2024 holdout");barplot(hold$MAE,names.arg=c("Lag model","Previous-year baseline"),col=c("#137E8D","#8198A4"),ylab="MAE (kBtu per square foot)",main="Same holdout population",ylim=c(0,max(hold$MAE)*1.2))
mtext("Independent public-data study. Predictors from the prior year only. No city endorsement.",outer=TRUE,line=0.4,cex=.8,col="#526978");dev.off()
print(metrics)
