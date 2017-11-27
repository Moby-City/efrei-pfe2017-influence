const { translate } = require('deepl-translator')
const fs = require('fs-extra')

const max = parseInt(process.argv[process.argv.length - 2])
const filename = process.argv[process.argv.length - 1]

if (process.argv.length < 3 || isNaN(max)) {
  console.log('Usage: translate.py NUM_TO_TRANSLATE IN_FILE.json')
  process.exit(1)
}

(async () => {
  let text = await fs.readFile(filename)
  let data = JSON.parse(text)
  let count = 0

  for (let article of data) {
    if (article.translated_text) continue
    console.log(`${article.title} (${count + 1}/${max})`)
    article.translated_text = (await translate(article.text, 'DE')).translation
    article.translated_title = (await translate(article.title, 'DE')).translation
    console.log(`\t=> ${article.translated_title}`)
    if (++count === max) break
  }

  fs.writeFile(filename, JSON.stringify(data, null, '  '))
})().catch(err => { throw err })
