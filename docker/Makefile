.PHONY: backup build clean run

build: Makefile
	# build vue.js app via npm and make
	# TODO currently not working on all machines due to babel/webpack/vue :(
	# rm -rf ../client/build
	# cd ../client && npm install
	# cd ../client && $(MAKE)
	# copy all source folders to this folder to build docker image
	mkdir client
	mkdir scripts
	rm -rf server ntg_common
	cp -a ../server ../ntg_common .
	cp -a ../client/build/* ./client
	cp -a ../scripts/cceh/* ./scripts
	# we need two dockerfiles, one for the db and one for the server
	docker build -f Dockerfile.db --tag=intf/ntg-db-server  .
	docker build -f Dockerfile    --tag=intf/ntg-app-server .

# this command only works on a production server with a fully functional database
backup:
	mkdir -p /tmp/backup
	pg_dump --format custom mark_ph31 -n ntg -T "ntg.original_*" -T "ntg.tmp_*" \
			--exclude-table-data="ntg.notes*" > /tmp/backup/mark_ph31.dump

run: build
	docker-compose up

cbgm: build
	docker-compose run ntg-app-server cbgm

# TODO integrate in gitlab registry of wwu.it
# push:
# 	cat ~/.dockerhubpass | docker login --username marcelloperathoner --password-stdin
# 	docker push cceh/ntg-app-server:latest
# 	docker push cceh/ntg-db-server:latest
# 	docker logout

clean:
	docker container stop $$(docker container ls -a -q)
	docker container rm   $$(docker container ls -a -q)
	docker network prune -f
	docker rmi -f $$(docker images --filter dangling=true -qa)
	docker volume rm $$(docker volume ls --filter dangling=true -q)
	docker rmi -f $$(docker images -qa)

clean-volume:
	docker-compose down --volumes
