# Aphrodite
A repository of emotional bot system

## Get Started

- None

## Something

- None

## Github Management

### Branch Management
- branch name
  - `feat`: Add features to existing documents
  - `doc`: Add documents
  - `hotfix`: Need hotfix some bugs
  - `release`: Complete release version

### Management command
- Before preceeding with the task
  - `git fetch`: Update local with origin/main
  - `git branch [-l / -r / -a]`: Lookup local/remote/all branches
  - `git pull origin <branch>`:  Get remote branch named "<branch>"
  - `git checkout origin/main`: Main remote branch
  - `git checkout -b <local branch> --track origin/main`: make branch named "<local branch>" with traking the main remote branch 

- After preceeding with the task
  - `git commit -m <message>`: Commit the local modifications with <message>
  - `git push origin <local branch>`: Push the local branch to origin 

- Additional
  `git stash`: Save the current modifications to cache
  `git stash apply`: Reload the modifications from cache


```bash
git fetch
git checkout -b feat/conversation_improvement --track origin/main
git branch --set-upstream-to origin/main
git add <something>
git commit -m "<something>"
git push origin feat/conversation_improvement

- PR in GIthub
git push origin --delete feat/conversation_improvement
git branch -D feat/conversation_improvement
```

## References
[meta-gpt](https://github.com/geekan/MetaGPT)
[agents](https://github.com/aiwaves-cn/agents#web-demos)
