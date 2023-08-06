make_GitHub_wiki_tree
=====================

make GitHub wiki tree

Package Documentation

 - GitHub wiki tree https://github.com/HatsuneMiku/make_GitHub_wiki_tree/wiki

 - GitHub repository https://github.com/HatsuneMiku/make_GitHub_wiki_tree

 - PyPI https://pypi.python.org/pypi/make_GitHub_wiki_tree


Usage
-----

```bash
git clone https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.wiki.git YOUR_REPOSITORY.wiki
cd YOUR_REPOSITORY.wiki
echo YOUR_ACCOUNT > mktree.cf
echo YOUR_REPOSITORY >> mktree.cf
mkdir 2014
mkdir 2014/201407
echo test > 2014/201407/20140711_0001.md
git add 2014/201407/20140711_0001.md
python mktree.py
git add Tree.md
git add _Sidebar.md
git commit -m 'make tree'
git push -u origin master
```
