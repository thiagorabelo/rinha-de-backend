
clean: clean-pg clean-redis

databases:
	docker compose up redis postgres

psql:
	# docker compose exec -u postgres postgres psql -U galo rinha_de_backend
	PGPASSWORD=cocorico psql -U galo -h localhost -p 5431 rinha_de_backend

# psql:
# 	docker compose exec postgres psql -U galo rinha_de_backend

down:
	docker compose down

clean-pg:
	docker compose exec -u postgres postgres psql -U galo -d rinha_de_backend -c "delete from pessoas_pessoa"

clean-redis:
	docker compose exec redis sh -c 'echo "flushall" | redis-cli'
