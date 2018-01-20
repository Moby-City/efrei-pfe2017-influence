library(dplyr)
library(tm)
library(rjson)
library(tidytext)
library(SnowballC)
library(wordcloud)
library(stringi)
library(RTextTools)
library(readr)

data <- read_delim("~/Downloads/2017-12-29-pickasso-twitter.txt", 
                                           "\t", escape_double = FALSE, col_names = FALSE, 
                                     trim_ws = TRUE)

  
stopw = stopwords(kind="fr")

teext = c()
for(i in 1:length(data[[1]])){
  txt = data[[1]][i]
  txt = gsub("http\\w+ *", "", txt)
  txt = gsub("https\\w+ *", "", txt)
  Encoding(txt) <- "UTF-8"
  txt = iconv(txt, "UTF-8", "UTF-8",sub='')
  teext[i] = txt
}
df = data.frame(txt=teext)

review_corpus <- Corpus(VectorSource(df$txt))

#Create the toSpace content transformer
toSpace <- content_transformer(function(x, pattern) {return (gsub(pattern," ",
                                                                  x))})
# Apply it for substituting the regular expression given in one of the former answers by " "
review_corpus<- tm_map(review_corpus,toSpace,"[^[:graph:]]")

review_corpus = tm_map(review_corpus, removeWords, stopwords("french"))
review_corpus = tm_map(review_corpus, removeWords, stopwords("english"))
review_corpus = tm_map(review_corpus, content_transformer(tolower))
review_corpus = tm_map(review_corpus, stemDocument, language = "french") 
review_corpus = tm_map(review_corpus, removePunctuation)
review_corpus = tm_map(review_corpus, removeNumbers)
review_corpus =  tm_map(review_corpus, stripWhitespace)

review_dtm_tfidf <- DocumentTermMatrix(review_corpus, control = list(weighting = weightTfIdf))
review_dtm_tfidf = removeSparseTerms(review_dtm_tfidf, 0.99)
review_dtm_tfidf
inspect(review_dtm_tfidf)
inspect(review_dtm_tfidf[1,1:20])

freq = data.frame(sort(colSums(as.matrix(review_dtm_tfidf)), decreasing=TRUE))
wordcloud(rownames(freq), freq[,1], max.words=100, colors=brewer.pal(1, "Dark2"))

target_words = rownames(freq)
remove = c("france","plus","paris","tous","the","pour","les","ans","faire","tout","aussi","comme","entre","fait",
           "comm","grand","franc","fair","jour","lion","rencontr","premi","auss","international","person",
           "france","facebook","vidéo","une","pour","'","mobilisnoo","aujourdhui","co…","…","nouvel",
           "soir","don","nous","journ","demain","par","http...","parl","bel","tres","équip","’","présent","plac")
target_words = target_words[!target_words %in% remove]
target_words = union(target_words,c("ong"))
target_words = union(target_words,c("encourag"))
target_words

df2 = data.frame(txt=review_corpus$content)
df2$y = 0

for(i in 1:length(df2$txt)){
  print(i)
  if(TRUE %in% stri_detect_fixed(df2[i,1],target_words)){
    df2[i,2]=1
  }
}

dtMatrix = create_matrix(df2$txt)

# configure training data
container <- create_container(dtMatrix, df2$y, trainSize=1:150000, virgin=FALSE)
# train a SVM Model
model <- train_model(container, "SVM", kernel="linear", cost=1)

# create data for prediction based on what was not used for training
predictionData = df2[150000:191000,1]
predictionData_trueTarget = df2[150000:191000,2]

# change RTextTools source code for R3.6
# Acronym -> acronym
trace("create_matrix", edit=T)

# create a prediction document term matrix
predMatrix <- create_matrix(predictionData, originalMatrix=dtMatrix)

# create the corresponding container
predSize = length(predictionData)
predictionContainer <- create_container(predMatrix, labels=rep(0,predSize), testSize=1:predSize, virgin=FALSE)

# predict
results <- classify_model(predictionContainer, model)
results$SVM_LABEL

true_positive =0
true_negative =0
false_positive=0
false_negative=0

for(i in 1:length(predictionData_trueTarget)){
  # if model predicted relevant
  if(results[i,1]==1){
    if(predictionData_trueTarget[i]==1){
      true_positive = true_positive+1      
    }else{
      false_positive= false_positive+1
    }
  }
  
  # if model predicted relevant
  if(results[i,1]==0){
    if(predictionData_trueTarget[i]==0){
      true_negative = true_negative+1      
    }else{
      false_negative= false_negative+1
    }
  }
  
}

true_positive
true_negative
false_negative
false_positive
