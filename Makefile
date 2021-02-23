run:
	docker-compose up -d

download:
	docker-compose run --rm freqtrade download-data \
		--config user_data/config.json \
		-t 1h \
		--days 500

backtest:
	docker-compose run --rm freqtrade backtesting \
		--config user_data/config.json \
		--strategy CourseStrategy \
		--timerange 20200101-

hyperopt:
	docker-compose run --rm freqtrade hyperopt \
		--config user_data/config.json \
		--hyperopt CourseHyperOpt \
		--hyperopt-loss SharpeHyperOptLoss \
		--strategy CourseStrategy \
		--timerange 20200101- \
		--stake-amount 0.01 \
		--print-all \
		--job-workers 8 \
		--epochs 100

compress:
	docker-compose run --rm freqtrade convert-data \
		--format-from json \
		--format-to jsongz \
		-t 1h
