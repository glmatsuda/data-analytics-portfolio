s <- readRDS("results/validation-state.rds")
stopifnot(max(s$train$target_year) < min(s$test$target_year))
stopifnot(all(s$test$previous_year==2023),all(s$test$target_year==2024))
stopifnot(!anyDuplicated(paste(s$test$id,s$test$target_year)))
stopifnot(all(is.finite(s$test$model_prediction)),all(s$test$model_prediction>=0))
stopifnot(nrow(s$test)==s$metrics$n[s$metrics$population=="2024 holdout"][1])
for (model in c("model_prediction","baseline_prediction")) {
  computed <- mean(abs(s$test$actual-s$test[[model]]))
  expected <- subset(s$metrics,population=="2024 holdout")$MAE[if(model=="model_prediction")1 else 2]
  stopifnot(abs(computed-expected)<1e-9)
}
cat("Energy model checks passed: temporal separation, prior-year predictors, unique keys, finite predictions, equal scoring population, independent MAE.\n")
