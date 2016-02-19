#loading Libraries
library(caret)
library(Hmisc)
library(randomForest)
library(pROC)
library(e1071)
library(klaR)
library(party)

#loading data in variable
mdata <- read.csv("D:\\Study Stuff\\Knowledge Discovery and Data Mining\\resources\\PakDD\\PAKDD2009.csv")

#filtering Some Columns
mdata$Reference1 <- NULL
mdata$Reference2 <- NULL
mdata$ProfessionCode <- NULL
mdata$AreaCode <- NULL
#print names of Columns
names(mdata)

#converting Label column to char type
mdata$Label <- as.character(mdata$Label)

#filtering missing value column
missingValuesCol <- which(colSums(is.na(mdata))>25000)
mdata <- mdata[,-c(missingValuesCol)]

#grabbing numeric data for normalizing in order to find low variance columns
numericData <- sapply(mdata,is.numeric)
numericData <- mdata[,c(numericData==TRUE)]

#normalization Function (Min,max)
normalizationFunction <- function(x){(x-min(x,na.rm=TRUE))/(max(x,na.rm = TRUE)-min(x,na.rm = TRUE))}
#normalizing Data
normdDat <- as.data.frame(lapply(numericData, normalizationFunction))
#Variance Function
varFunc <- function(v){var(v, na.rm=TRUE)}
#variance vector
varianceVector <-  as.data.frame(lapply(normdDat, varFunc))

#Finding low variance column names
namesOfLowVarianceColumns <- which(varianceVector[1,] <= 0.02)
namesOfLowVarianceColumns <- names(normdDat[,namesOfLowVarianceColumns])

#Filtering Low variance Columns
for (v in namesOfLowVarianceColumns) {
  
  mdata[[v]] <- NULL
  
}

#Converting Lable to Factor
mdata$Label <- as.factor(mdata$Label)

#Calculating Corelation Matrix.
corMat <- cor(mdata[,which(sapply(mdata, is.numeric))], method = "pearson")

#Calculating and replacing missing values
for (i in 1:ncol(mdata)) {
    if (is.numeric(mdata[,i])) {
      mdata[is.na(mdata[,i]),i] <- median(mdata[,i],na.rm = TRUE)
    }
  else{
    mdata[is.na(mdata[,i]),i] <- NA
  }
}

#checking column names and there classes(type)
sapply(mdata,class)

#Partitioning Data
set.seed(1234)
ind <- sample(2,nrow(mdata),replace = TRUE, prob = c(0.7,0.3))
trainData <- mdata[ind==1,]
testData <- mdata[ind==2,]

#Training and predicting Naive Bayes
naiv <- naiveBayes(Label ~ ., data = trainData )
pred <- predict(naiv, newdata = testData)
#Table for prediction
table(pred,testData$Label)
#ROC for Naive Bayes
roc(pred,as.numeric(testData$Label), percent=TRUE, plot=TRUE, ci=TRUE)

#Training and predicting Via Random Forest
rf <- randomForest(Label ~ .,data = trainData, ntree = 150, importance = TRUE)
predRF <- predict(rf, newdata = testData)
#ROC for Random Forest
roc(predRF,as.numeric(testData$Label), percent=TRUE, plot=TRUE, ci=TRUE)

#roc(pred,testData$Label,plot = TRUE)
#roc(predRF,testData$Label,plot = TRUE)

#gathering column names on basis of there types
#intVars <- names(mdata[sapply(mdata, class)=="integer"])
#factorVars <- names(mdata[sapply(mdata, class)=="factor"])
#numericVars <- names(mdata[sapply(mdata, class)=="numeric"])
#sapply(mdata, class)
#mdata$Label <- as.factor(mdata$Label)

