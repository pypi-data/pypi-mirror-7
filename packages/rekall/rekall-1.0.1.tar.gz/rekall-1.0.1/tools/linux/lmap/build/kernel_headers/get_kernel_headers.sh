#usr/bin/env bash

RELEASE=3.13.0-29-generic
KBUILD="/lib/modules/$RELEASE/build";
NEW_KBUILD=/home/scudette/rekall/tools/linux/lmap/build/kernel_headers

# link all contents of kbuild, but copy config
for FILE in `ls -AHL $KBUILD`
do
  if [ $FILE == ".config" ]
  then
    # Copy the config, we need to modify this later
    cp $KBUILD/$FILE $NEW_KBUILD
  else
    ln -s $KBUILD/$FILE $NEW_KBUILD
  fi
done

