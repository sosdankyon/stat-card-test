[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![kr](https://img.shields.io/badge/lang-kr-green.svg)](README.kr.md)

---

# my-github-stats
프로필 페이지에 표시할 수 있는 깃허브 상태 카드를 자동으로 생성 및 갱신해주는 레포지토리.

## 사용법
### 프로필 레포지토리 준비
자신의 깃허브 사용자 이름과 동일한 이름의 레포지토리를 만들고 `README.md` 파일을 만든다.
이 파일 안에 적힌 내용은 자신의 깃허브 프로필 페이지 메인에 표시된다.

스탯 카드를 표시하고 싶은 위치에 `!()[my-github-stats.svg]`라고 작성한다.

### 토큰 발급
`Fine-grained tokens` 생성
* `Repository access`를 `All repositories`로 설정
* `Repositories` 권한 중 `Contents` 권한 추가
  * `Contents`의 `Access`를 `Read and write`로 변경
* `Expiration`은 `No expiration`으로 설정

생성된 토큰은 메모해둔다.

### 레포지토리 설정
이 레포지토리를 포크한다.

`Repository secrets` 추가
* `TOKEN`: (필수) 위에서 생성한 토큰

`Repository variables` 추가
* `USER_NAME`: (필수) 자신의 사용자 이름
* `FONT`: (선택) 스탯 카드에 사용할 웹 폰트의 url 또는 레포지토리의 루트를 기준으로 하는 상대 경로
  * url인 경우 반드시 `https://`로 시작해야함
  * 입력하지 않으면 기본 폰트가 사용됨

### 카드 갱신
레포지토리의 `Actions`에서 워크플로우 `Update card`를 수동으로 실행하여 오류 발생 여부를 확인한다.
오류 없이 실행됐다면 프로필 레포지토리에 `my-github-statss.svg`파일이 생성됨.

기본적으로 매일 0시에 자동으로 갱신됨.

## 주의사항
* 폰트는 `woff` 또는 `woff2` 포맷을 권장하며, 폰트 라이센스에 주의
  * 폰트 라이센스 미준수(특히 임베딩 및 배포 관련)로 인한 문제에 대해서는 당사자가 책임져야함
  * 기본 폰트는 [둥근모꼴](https://noonnu.cc/font_page/250)이며, ascii 코드만 포함하도록 수정됨
  * 폰트를 변경할 경우 `template.svg`에서 글자의 위치를 조정해야될 가능성 있음