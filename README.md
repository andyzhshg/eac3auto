# eac3 auto convert 

This scrip using ffmpeg to add an aac/ac3 audio stream to a video only has eac3 audio stream. 

This make videos can be played on devices which can not decode eac3 audios. 

## 1. convert a single file

```bash
docker run --name container_name -v/your/video/path:/videos eac3auto file /video/video.mp4
```

## 2. convert a directory

```bash
docker run --name container_name -v/your/video/path:/videos eac3auto directory /video
```

## 3. convert a directory and watch incoming files

```bash
docker run --name container_name -v/your/video/path:/videos eac3auto run_watch /video/video.mp4
```

## 4. watch a directory for incoming files

```bash
docker run --name container_name -v/your/video/path:/videos eac3auto watch /video/video.mp4
```
