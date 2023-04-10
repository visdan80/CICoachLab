#!/bin/bash
# This file takes the bitlocked device defined in the path provided first argument mounts it to the
# path defined in the second argument. The decrypted data are mounted to the path defined in the third argument.
# the hardcoded password just provides a moderate security level which appears to be reasonably secure to protect the
# study subject data  which will be gathered by the subject
# and will be transported on a defined USB memory stick for transportation from the patient PC to the
# clinical institution.
# The hard coded password will be different in the

# Until a higher security level will be implemented and can be applied in the workflow which might use a gpg
# implementation with two pairs of public and private keys this security level will suffice.
# TODO: Implement a higher level of security

: <<'EnddOfBlockComment'

Copyright (C) 2019-2022 Daniel Leander

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
EnddOfBlockComment

source=$1
mountPathEncrypted=$2
mountPathClear=$3

# unlockCICoachStick.sh $source $keyFile $#mountPathEncrypted $mountPathClear
sudo dislocker -V  "$source"  -u12345678    --  "$mountPathEncrypted"
if [ $? -ne 0 ]; then
  echo 'dislocker: encrypted mount failed: ' "$source" "$mountPathEncrypted"
  exit 1
fi
sudo mount -o loop "$mountPathEncrypted"'dislocker-file' "$mountPathClear"
if [ $? -ne 0 ]; then
  echo 'dislocker: decrypted mount failed:' "$mountPathEncrypted" "$mountPathClear"
  exit 2
fi

sudo  chmod -R 777  "$mountPathClear"
if [ $? -ne 0 ]; then
  echo 'changing user access rights failed'
  exit 3
fi

echo 'Nothing failed'
exit 0
