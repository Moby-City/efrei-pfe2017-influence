# Class for Predicting if a Text is related to associations or not based on Twitter
# Results:  1 - related to associations
#           0 - not related to associations 
# Example Call on Console: Rscript --vanilla SVM_predict.R je suis une baguette.

#!/usr/bin/Rscript
library(dplyr)
library(tm)
library(rjson)
library(tidytext)
library(SnowballC)
library(wordcloud)
library(stringi)
library(RTextTools)
library(readr)

createMatrix <- function (textColumns, language = "english", minDocFreq = 1, 
          maxDocFreq = Inf, minWordLength = 3, maxWordLength = Inf, 
          ngramLength = 1, originalMatrix = NULL, removeNumbers = FALSE, 
          removePunctuation = TRUE, removeSparseTerms = 0, removeStopwords = TRUE, 
          stemWords = FALSE, stripWhitespace = TRUE, toLower = TRUE, 
          weighting = weightTf) 
{
  stem_words <- function(x) {
    split <- strsplit(x, " ")
    return(wordStem(unlist(split), language = language))
  }
  tokenize_ngrams <- function(x, n = ngramLength) return(rownames(as.data.frame(unclass(textcnt(x, 
                                                                                                method = "string", n = n)))))
  control <- list(bounds = list(local = c(minDocFreq, maxDocFreq)), 
                  language = language, tolower = toLower, removeNumbers = removeNumbers, 
                  removePunctuation = removePunctuation, stopwords = removeStopwords, 
                  stripWhitespace = stripWhitespace, wordLengths = c(minWordLength, 
                                                                     maxWordLength), weighting = weighting)
  if (ngramLength > 1) {
    control <- append(control, list(tokenize = tokenize_ngrams), 
                      after = 7)
  }
  else {
    control <- append(control, list(tokenize = scan_tokenizer), 
                      after = 4)
  }
  if (stemWords == TRUE && ngramLength == 1) 
    control <- append(control, list(stemming = stem_words), 
                      after = 7)
  trainingColumn <- apply(as.matrix(textColumns), 1, paste, 
                          collapse = " ")
  trainingColumn <- sapply(as.vector(trainingColumn, mode = "character"), 
                           iconv, to = "UTF8", sub = "byte")
  corpus <- Corpus(VectorSource(trainingColumn), readerControl = list(language = language))
  matrix <- DocumentTermMatrix(corpus, control = control)
  if (removeSparseTerms > 0) 
    matrix <- removeSparseTerms(matrix, removeSparseTerms)
  if (!is.null(originalMatrix)) {
    terms <- colnames(originalMatrix[, which(!colnames(originalMatrix) %in% 
                                               colnames(matrix))])
    weight <- 0
    if (attr(weighting, "acronym") == "tf-idf") 
      weight <- 1e-09
    amat <- matrix(weight, nrow = nrow(matrix), ncol = length(terms))
    colnames(amat) <- terms
    rownames(amat) <- rownames(matrix)
    fixed <- as.DocumentTermMatrix(cbind(matrix[, which(colnames(matrix) %in% 
                                                          colnames(originalMatrix))], amat), weighting = weighting)
    matrix <- fixed
  }
  matrix <- matrix[, sort(colnames(matrix))]
  gc()
  return(matrix)
}



args = commandArgs(trailingOnly=TRUE)
if (length(args)==0) {
  stop("No text provided", call.=FALSE)
} else{
  # default output file
  txt = paste(args, collapse = ' ')
}

# load Model and Container
target_words = load(file="target_words.rda")
model = readRDS(file = "SVM_model.rds")
dtMatrix = readRDS(file="dtMatrix.rds")

# Preprocess Text
txt = gsub("http\\w+ *", "", txt)
txt = gsub("https\\w+ *", "", txt)
Encoding(txt) <- "UTF-8"
txt = iconv(txt, "UTF-8", "UTF-8",sub='')

txt_corpus <- Corpus(VectorSource(txt))
#Create the toSpace content transformer
toSpace <- content_transformer(function(x, pattern) {return (gsub(pattern," ",
                                                                  x))})
# Apply it for substituting the regular expression given in one of the former answers by " "
txt_corpus<- tm_map(txt_corpus,toSpace,"[^[:graph:]]")
txt_corpus = tm_map(txt_corpus, removeWords, stopwords("french"))
txt_corpus = tm_map(txt_corpus, removeWords, stopwords("english"))
txt_corpus = tm_map(txt_corpus, content_transformer(tolower))
txt_corpus = tm_map(txt_corpus, stemDocument, language = "french") 
txt_corpus = tm_map(txt_corpus, removePunctuation)
txt_corpus = tm_map(txt_corpus, removeNumbers)
txt_corpus = tm_map(txt_corpus, stripWhitespace)

df2 = data.frame(txt=txt_corpus$content)

#trace("create_matrix", edit=T)
predictionData = df2[1,1]

print(predictionData)

predMatrix <- createMatrix(predictionData, originalMatrix=dtMatrix)

# create the corresponding container
predSize = length(predictionData)
predictionContainer <- create_container(predMatrix, labels=rep(0,predSize), testSize=1:predSize, virgin=FALSE)

# predict
results <- classify_model(predictionContainer, model)

print(results$SVM_LABEL)
