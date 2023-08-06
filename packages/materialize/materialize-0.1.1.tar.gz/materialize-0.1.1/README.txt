===========
Materialize
===========

Materialize is a simple toolkit for replacing env files with etcd configurations. 

Step #1: Manually (or via a docker environment setting from the docker command line DO NOT BAKE IN!)

	export etchost={host of etcd server}
	export etccluster{dev/prod/uat}

Step #2: Edit the .env file so anything that has to go into shared config (between apps on a cluster) has #common after it. Then type the following;-

	./materialize dematerialize {cluster} {appname}

With the .env file now scanned into etcd the app is ready to go.

Two options

1) Reconstruct .env from the command line in the container. The cluster is gleaned from the environment variable.

	./materialize magic {appname} 

2) Insert the following into manage.py in the django.

	import materializer
	materializer.magic_rematerializer()

And let the magic take hold.

