set -e
gh repo view glw907-test/cleanroom-probe > /dev/null 2>&1 || gh repo create glw907-test/cleanroom-probe --public
gh auth setup-git
git clone https://github.com/glw907-test/cleanroom-probe pushtest
cd pushtest
git checkout -b probe-@NAME@
git -c user.name=probe -c user.email=probe@example.invalid commit --allow-empty -m probe
git push origin probe-@NAME@
git push origin --delete probe-@NAME@
