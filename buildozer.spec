name: Build APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          sudo apt update
          sudo apt install python3-pip openjdk-17-jdk unzip -y
          pip3 install buildozer cython

      - name: Accept Android SDK licenses
        run: |
          yes | $ANDROID_HOME/tools/bin/sdkmanager --licenses
        env:
          ANDROID_HOME: /usr/local/android-sdk

      - name: Build APK
        run: |
          buildozer android debug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: rampage
          path: bin/*.apk
