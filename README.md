[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)
[![kr](https://img.shields.io/badge/lang-kr-green.svg)](README.kr.md)

---

# my-github-stats
프로파일에 페이지에 표시할 수 있는 깃허브 상태 카드를 자동으로 갱신해주는 레포지토리다.

## 사용법
### 프로필 레포지토리 준비
자신의 깃허브 사용자 이름과 동일한 이름의 레포지토리를 만들고 `README.md` 파일을 만든다.
이 파일 안에 적힌 내용은 자신의 깃허브 프로필 페이지 메인에 표시된다.

스탯 카드를 표시하고 싶은 위치에 `!()[my-github-stats.svg]`라고 작성한다.

### 토큰 발급
`Fine-grained tokens`을 아래와 같이 생성한다

* `Repository access`를 `All repositories`로 설정
* `Permissions`에서 `Repositories` 권한 중 `Contents` 권한을 추가
  * `Contents`의 `Access`를 `Read and write`로 변경 

토큰이 만료되지 않도록 `Expiration`은 `No expiration`으로 설정하고 토큰을 생성 후 복사하여둔다.

### 레포지토리 설정
이 레포지토리를 포크한다.

다음과 같은 `Repository secrets`을 추가한다.
* `FONT`: 스탯 카드에 사용할 웹 폰트의 url 또는 레포지토리의 루트를 기준으로 하는 상대 경로
* `TOKEN`: 위에서 생성한 토큰
* `USER_NAME`: 자신의 사용자 이름

### 카드 갱신
레포지토리의 `Actions`에서 워크플로우 `Update card`를 수동으로 실행하여 오류 발생 여부를 확인한다.
오류가 없이 실행됐다면 프로필 레포지토리에 `my-github-statss.svg`파일이 생성될것이다.

이후 기본적으로 매일 0시에 자동으로 갱신될것이다.

## 주의사항
* 갱신 간격을 조정하려면 포크한 이 레포지토리의 `.github/workflows/main.yml`에서 `cron`값을 적절히 수정한다.
* 폰트는 `woff` 또는 `woff2` 포맷을 권장하며 사용시 라이센스에 주의한다.
  * 폰트 라이센스 미준수(특히 임베딩, 배포 관련)로 인한 문제에 대해서는 당사자가 책임져야한다.
  * 기본 폰트는 [둥근모꼴](https://noonnu.cc/font_page/250)이며, 폰트를 변경할 경우 `template.svg`에서 글자의 좌표를 수정해야할 수 있다.