#!/usr/bin/env bash

echo 'Starting Build'; sleep 1

echo 'Creating Zip file from package';  sleep 1

zip -r9 mget __main__.py Mget -x \*.pyc

echo 'Done Zipping files'; sleep 1
echo 'Writting to mget'; sleep 1

echo '#!/usr/bin/env python3' > mget
cat mget.zip >> mget

echo 'Done Writting File mget'; sleep 1
rm -fr mget.zip
chmod +x mget

echo 'Creating a link /usr/local/bin/mget'
cp mget /usr/local/bin/mget
echo 'Thanks for installing MGet.'
