## Purpose
The purpose of this project is to increase the ability to reverse smart contract function hashes when reversing contracts or interacting with contracts without an ABI. 

### Strategy
Scraping data from Google Big Query is a popular method for ingesting large amounts of application related data. In this case, we ingested all .sol files within Github and extracted the function defintions. We used two queries (included below). 

After extracting the data, we parsed the definitions and converted them to function hashes using a naive/simplistic parsing script. Improving the parsing script is expected to yield around 2-3x more hashes as currently types such as nested arrays and mappings are not supported. 

### Results
We were able to add over 400 new potential hashes to the [4byte signature database](https://www.4byte.directory/). Such a small amount of new hashes either indicates that parsing needs to be improved or this strategy has already been implemented before.

### Future Improvements
Extracting function definitions from other type langages (C#, TypeScript, Golang, etc) and converting them to their solidity equivalent could expose new hashes that may not exist in public repositories but are likely to exist as developers may use similar naming conventions.

#### Queries

Data generated with the following queries. Unfortunately, the github language sources did not allow matching on solidity (or at least I could not get it to work). Therefore, the actual matches probably have plenty of false positives. 

```
SELECT
  files.repo_name, files.path,ARRAY_TO_STRING(REGEXP_EXTRACT_ALL(contents.content, 'function\\s+([a-zA-Z_-]+\\(.*?\\))'),';')
FROM
  `bigquery-public-data.github_repos.files` files
LEFT JOIN
  `bigquery-public-data.github_repos.contents` contents
ON
  files.id = contents.id
WHERE
    ENDS_WITH(files.path, ".sol")
    AND NOT contents.binary
    AND regexp_contains(contents.content, 'function[(].*[)]')
    AND regexp_contains(contents.content, '[cC]ontract')
```

```
SELECT
  files.repo_name, files.path,ARRAY_TO_STRING(REGEXP_EXTRACT_ALL(contents.content, 'function\\s+([a-zA-Z_-]+\\(.*?\\))'),';')
FROM
  `bigquery-public-data.github_repos.files` files
LEFT JOIN
  `bigquery-public-data.github_repos.contents` contents
ON
  files.id = contents.id
WHERE
    ENDS_WITH(files.path, ".sol")
    AND NOT contents.binary
    AND regexp_contains(contents.content, '[cC]ontract'
```
