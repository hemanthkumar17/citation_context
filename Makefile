.PHONY: extr extr_bib parse

all: extr parse_text mine

extr:
	python3 arxiv_extr.py

parse:
	java -cp ./cermine/cermine-impl/target/cermine-impl-1.14-SNAPSHOT-jar-with-dependencies.jar pl.edu.icm.cermine.ContentExtractor -path /root/citation_context/arxiv_sample -outputs bibtex

parse_text:
	java -cp ./cermine/cermine-impl/target/cermine-impl-1.14-SNAPSHOT-jar-with-dependencies.jar pl.edu.icm.cermine.ContentExtractor -path /root/citation_context/arxiv_sample -outputs jats

extr_bib:
	python3 arxiv_extr_from_bib.py

clean:
	rm -rf arxiv_mine

mine:
	python3 jats_utils.py

fresh: clean all