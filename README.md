# Aphrodite
A repository of emotional bot system

## Get Started

- None

## Something

- None

## Branch Management

깃헙 관리 방식

브랜치 관리

- 이름명
  - `feat`: 기능이 추가될 때
  - `doc`: 문서가 추가될 때
  - `hotfix`: 급하게 오류가 수정되어야 할 때
  - `release`: 버전 완성될 때
 
- 방식
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
