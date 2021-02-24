run:
	docker-compose up -d

download:
	docker-compose run --rm freqtrade download-data \
		--config user_data/config.json \
		-t 15m \
		--days 500

backtest:
	docker-compose run --rm freqtrade backtesting \
		--config user_data/config.json \
		--strategy CourseStrategy \
		--timerange 20200101-

hyperopt:
	docker-compose run --rm freqtrade hyperopt \
		--config user_data/config.json \
		--hyperopt CourseHyperopt \
		--hyperopt-loss SharpeHyperOptLoss \
		--strategy CourseStrategy \
		--timerange 20200101- \
		--stake-amount 0.02 \
		--job-workers 1 \
		--epochs 1000

hyperopt_roi:
	docker-compose run --rm freqtrade hyperopt \
		--config user_data/config.json \
		--hyperopt EmptyHyperopt \
		--hyperopt-loss SharpeHyperOptLossDaily \
		--spaces roi stoploss trailing \
		--strategy CourseStrategy \
		--timerange 20200101- \
		--stake-amount 0.02 \
		--job-workers 8 \
		--epochs 250
