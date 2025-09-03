[![en](https://img.shields.io/badge/lang-en-red.svg)](README.kr.md)
[![kr](https://img.shields.io/badge/lang-kr-green.svg)](README.kr.md)

---

# my-github-stats
A repository that automatically generates and updates GitHub stats cards for you to display on your profile page.

## How to Use
### Prepare Your Profile Repository
Create a new repository with the same name as your GitHub username and create a `README.md` file within it.
This is a special repository, and the content of its README will be displayed on your public GitHub profile page.

In the location where you want to display the stats card, add the following line: `![stat](my-github-stats.svg)`

### Generate a Token
#### Fine-grained tokens
> [\!WARNING]
> Currently, Fine-grained tokens cannot collect information from collaborator and organization repositories.

* Set `Repository access` to `All repositories`.
* Under `Repositories` permissions, add `Contents`.
    * Change the `Access` for `Contents` to `Read and write`.
* Set `Expiration` to `No expiration`.

#### Classic Token
* Check all boxes under the `repo` scope (5 total).
* Under `admin:org`, check `read:org`.
* Set `Expiration` to `No expiration`.

### Repository Setup
Fork this repository.

Add `Repository secrets`:
* `TOKEN`: (Required) The token you generated above.

Add `Repository variables`:
* `USER_NAME`: (Required) Your GitHub username.
* `FONT`: (Optional) The URL of a web font to use for the stats card, or a relative path from the repository's root.
    * If using a URL, it must start with `https://`.
    * If left blank, the default font will be used.

### Updating the Card
Go to the `Actions` tab of your forked repository, first enable the workflow, and then manually run the `Update card` workflow to check for any errors.
If it runs without errors, a `my-github-stats.svg` file will be generated in your profile repository.

By default, the card will be updated automatically around 00:00 (midnight) every day.

## Important Notes
* It is recommended to use fonts in `woff` or `woff2` format. Please be mindful of the font's license.
    * You are responsible for any issues arising from non-compliance with the font license (especially regarding embedding and distribution).
    * The default font is [Fixedsys](https://github.com/kika/fixedsys), which has been modified to include only ASCII characters.
* If you change the font, you may need to adjust the text positions in the `template.svg` file.