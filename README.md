# 成语接龙 IdiomGraph-gv

(This project doesn't make sense in English.)

成语接龙表。使用`graphviz`实现。

## Usage

1. Create a conda environment with the required packages:

```shell
conda create --name idiom --file conda-requirements.txt
conda activate idiom
```

2. Run this command to retrieve a list of idioms:

```shell
curl https://raw.githubusercontent.com/fighting41love/funNLP/master/data/%E6%88%90%E8%AF%AD%E8%AF%8D%E5%BA%93/ChengYu_Corpus%EF%BC%885W%EF%BC%89.txt > idioms.txt
```

3. Run the main script:

```shell
python main.py generate
```

## References

类似的项目有[IdiomGraph](https://github.com/shawlu95/IdiomGraph)——使用neo4j实现的。