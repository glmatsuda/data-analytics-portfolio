stopifnot(unname(tools::md5sum("data/source.csv")) == trimws(readLines("data/source.md5")))
# First run python prepare.py (or use python run.py for the whole workflow).
d <- read.csv("results/daily.csv",stringsAsFactors=FALSE,na.strings="")
d$date <- as.Date(d$date)
d$t <- as.numeric(d$date-as.Date("2022-01-01"))/365.25
d$sin1 <- sin(2*pi*d$t);d$cos1 <- cos(2*pi*d$t)
d$sin2 <- sin(4*pi*d$t);d$cos2 <- cos(4*pi*d$t)
d$weekday <- factor(d$weekday,levels=1:7,labels=c("Mon","Tue","Wed","Thu","Fri","Sat","Sun"))
clean <- subset(d,complete_day==1 & is.finite(crossings))
train <- subset(clean,year<=2023); test <- subset(clean,year==2024)
stopifnot(nrow(train)>300,nrow(test)>100,max(train$date)<min(test$date))
fit_model <- function(data) glm(crossings ~ weekday + sin1 + cos1 + sin2 + cos2 + t,family=quasipoisson(link="log"),data=data)
baseline <- function(training,newdata) {
  weekday_mean <- tapply(training$crossings,training$weekday,mean)
  unname(weekday_mean[as.character(newdata$weekday)])
}
score <- function(actual,prediction,label,population) data.frame(population=population,model=label,n=length(actual),MAE=mean(abs(actual-prediction)),RMSE=sqrt(mean((actual-prediction)^2)))
# One fixed calendar-year holdout. No test-year counts enter model features.
dev <- subset(train,year==2022);validation <- subset(train,year==2023)
dev_fit <- fit_model(dev);fit <- fit_model(train)
test$model_prediction <- as.numeric(predict(fit,newdata=test,type="response"));test$baseline_prediction <- baseline(train,test)
metrics <- rbind(score(validation$crossings,predict(dev_fit,newdata=validation,type="response"),"Calendar quasi-Poisson","2023 validation"),
  score(validation$crossings,baseline(dev,validation),"Training weekday mean","2023 validation"),
  score(test$crossings,test$model_prediction,"Calendar quasi-Poisson","2024 holdout"),
  score(test$crossings,test$baseline_prediction,"Training weekday mean","2024 holdout"))
write.csv(metrics,"results/metrics.csv",row.names=FALSE)
write.csv(test[,c("date","crossings","weekday","model_prediction","baseline_prediction")],"results/predictions.csv",row.names=FALSE)
write.csv(data.frame(term=names(coef(fit)),estimate=unname(coef(fit))),"results/coefficients.csv",row.names=FALSE)
write.csv(data.frame(split=c("train","validation","holdout"),first_date=c(as.character(min(train$date)),as.character(min(validation$date)),as.character(min(test$date))),last_date=c(as.character(max(train$date)),as.character(max(validation$date)),as.character(max(test$date))),n=c(nrow(train),nrow(validation),nrow(test))),"results/split-audit.csv",row.names=FALSE)
write.csv(data.frame(diagnostic="Quasi-Poisson dispersion",value=summary(fit)$dispersion),"results/diagnostics.csv",row.names=FALSE)
saveRDS(fit,"results/mobility-model.rds");saveRDS(list(train=train,test=test,metrics=metrics),"results/validation-state.rds")
capture.output(sessionInfo(),file="results/session-info.txt")
png("results/model-diagnostics.png",width=1600,height=1000,res=130,type=if (Sys.info()[["sysname"]]=="Darwin") "quartz" else "cairo")
par(mfrow=c(2,1),mar=c(4,5,3,2),bg="#F3F6F8",col.axis="#526978",col.lab="#172C3C",col.main="#172C3C")
plot(test$date,test$crossings,type="l",col="#8198A4",xlab="2024 holdout date",ylab="Recorded crossings per complete day",main="Observed crossings and calendar-model prediction");lines(test$date,test$model_prediction,col="#137E8D",lwd=2);legend("topleft",c("Observed","Model"),col=c("#8198A4","#137E8D"),lty=1,bty="n")
hold <- subset(metrics,population=="2024 holdout");barplot(hold$MAE,names.arg=c("Calendar quasi-Poisson","Training weekday mean"),col=c("#137E8D","#8198A4"),ylab="MAE (crossings/day)",main="Baseline comparison on identical complete days",ylim=c(0,max(hold$MAE)*1.2));dev.off()
print(metrics)
