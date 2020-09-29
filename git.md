# Git 命令



## 工作区上的操作

**新建仓库**

```git
git init 		# 初始化仓库
git clone url 	# 克隆仓库 
```

**提交（到暂存区）**

```git
git add . 				# 提交所有文件
git add <file1> <file2> # 提交指定文件
git add [dir]			# 提交指定文件夹
```

**查看信息**

```git
git status 			# 查看工作区所有文件状态
git diff <FileName> # 当前文件与暂存区中的不同
```



## 暂存区上的操作

**提交到版本库**

```git
git commit -m 'commit-info'
```

**撤销提交**

```git
git commit --amend
```

**查看信息 (比较版本)**

```git
git diff --cached				# 查看暂存区与本地仓库中文件的不同
git diff <FileName> --cached	# 指定文件
```



## 分支管理

**创建分支**

```git 
git branch <NewBranchName>
```

**查看本地和远程所有分支**

```git
git branch -a
```

**切换分支**

```git
git checkout <BranchName> 
git switch <BranchName> # 推荐
```

**推送本地分支到远程分支**

```git
git push origin <LocalBranch>:<RemoteBranch>
git push origin :<RemoteBranch>  # 推送本地空分支到远程分支（等同于删除远程分支）
```

**删除分支**

```git
git push origin -d <BranchName>	# 远程
git branch -d <BranchName>		# 本地
```

**分支合并**

```git
git merge <BranchName>  # 将指定分支合并到当前分支
```



