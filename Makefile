run:
	docker-compose up -d

download:
	docker-compose run --rm freqtrade download-data \
		-t 1h \
		--days 1000 \
		$(ARGS)

backtest:
	docker-compose run --rm freqtrade backtesting \
		--strategy CourseStrategy \
		$(ARGS)

hyperopt:
	docker-compose run --rm freqtrade hyperopt \
		--hyperopt CourseHyperOpt \
		--hyperopt-loss SharpeHyperOptLoss \
		--strategy CourseStrategy \
		--ticker-interval 1h \
		--config user_data/config.json \
		-j 2
