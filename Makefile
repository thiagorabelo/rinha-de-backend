
clean: clean-pg clean-redis

up:
	docker compose up

down:
	docker compose down

databases:
	docker compose up redis postgres pgbouncer

build-app:
	docker compose build app1

psql:
	# docker compose exec -u postgres postgres psql -U galo rinha_de_backend
	PGPASSWORD=cocorico psql -U galo -h localhost -p 5431 rinha_de_backend

# psql:
# 	docker compose exec postgres psql -U galo rinha_de_backend

clean-pg:
	docker compose exec -u postgres postgres psql -U galo -d rinha_de_backend -c "delete from pessoas_pessoa"

clean-redis:
	docker compose exec redis sh -c 'echo "flushall" | redis-cli'
