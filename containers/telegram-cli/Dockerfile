FROM ubuntu:focal
ENV DEBIAN_FRONTEND="noninteractive"

RUN apt-get update
RUN apt-get install -y build-essential git
RUN apt-get install -y libreadline-dev libconfig-dev libssl-dev lua5.2 liblua5.2-dev libevent-dev libjansson-dev python3-dev libgcrypt20-dev libssl-dev

WORKDIR /app
RUN  git clone --recursive https://github.com/vysheng/tg.git

WORKDIR /app/tg
RUN ./configure --disable-openssl --prefix=/usr CFLAGS="$CFLAGS -w"
RUN make

CMD /app/tg/bin/telegram-cli --json -P 4458