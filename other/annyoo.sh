if [ -d "/jd" ]; then
  root=/jd
else
  root=/ql
fi

if [ ! -f $root/config/Annyoo ]; then
  echo "未找到密钥文件，请在$root/config/存放密钥后重新执行命令"
else
  if [ ! -d ~/.ssh ]; then
    mkdir ~/.ssh
  fi
  mv $root/config/Annyoo ~/.ssh/
  chmod 0600 ~/.ssh/Annyoo
  echo -e 'Host github_Annyoo\nHostname github.com\nIdentityFile=/root/.ssh/Annyoo'>> ~/.ssh/config
  ssh -T git@github_Annyoo
fi