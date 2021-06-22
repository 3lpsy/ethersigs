
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
