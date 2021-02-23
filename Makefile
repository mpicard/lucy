run:
	docker-compose up -d

download:
	docker-compose run --rm freqtrade download-data \
		-t 15m \
		--days 500 \
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
		--stake-amount 0.01 \
		--timerange 20200101-20211231 \
		-j 8 \
		-e 1000
