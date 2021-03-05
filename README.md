# Stdchecker
Stdchecker is a Python library for checking the latest revisions of standard methods published by standard bodies. Supported standard bodies are:
- ASTM - American Society for Testing and Materials
- IEC - The International Electrotechnical Commission
- IEEE - The Institute of Electrical and Electronics Engineers
- TSE - Turkish Standards Institution (Türk Standardları Enstitüsü)

## Requirements
- Python 3.8+

## Installation
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install stdchecker:

```bash
pip install stdchecker
```
or directly from the source code:
```bash
git clone https://github.com/emreture/stdchecker.git
cd stdchecker
python setup.py install
```

## Usage
Fetching standard methods data:

```python
import stdchecker

std_list = ['D92', 'D93']

for i in stdchecker.fetch_astm(std_list):
    print(i)
```
Output:
```python
{'query': 'D92',
 'error': None,
 'no': 'ASTM D92',
 'rev': '18',
 'desc': 'Standard Test Method for Flash and Fire Points by Cleveland Open Cup Tester',
 'body': 'astm',
 'url': 'https://www.astm.org/Standards/D92.htm'}

{'query': 'D93',
 'error': None,
 'no': 'ASTM D93',
 'rev': '20',
 'desc': 'Standard Test Methods for Flash Point by Pensky-Martens Closed Cup Tester',
 'body': 'astm',
 'url': 'https://www.astm.org/Standards/D93.htm'}
```
Checking if existing standard methods are up-to-date:
```python
import stdchecker

std_list = ['D92', 'D93']
actual_std_list = [
    {'no': 'ASTM D92', 'rev': '18'},
    {'no': 'ASTM D93', 'rev': '18'}
]

fetch_generator = stdchecker.fetch_astm(std_list)
for i in stdchecker.check_astm(fetch_generator, actual_std_list):
    print(i)
```
Output:
```python
{'query': 'D92',
 'error': None,
 'no': 'ASTM D92',
 'rev': '18',
 'desc': 'Standard Test Method for Flash and Fire Points by Cleveland Open Cup Tester',
 'body': 'astm',
 'url': 'https://www.astm.org/Standards/D92.htm',
 'check': True,
 'actual': '18'}

{'query': 'D93',
 'error': None,
 'no': 'ASTM D93',
 'rev': '20',
 'desc': 'Standard Test Methods for Flash Point by Pensky-Martens Closed Cup Tester',
 'body': 'astm',
 'url': 'https://www.astm.org/Standards/D93.htm',
 'check': False,
 'actual': '18'}
```
If an `id` is provided (for example existing standard methods are stored in a database), the output will also include the `id` key and its value:
```python
import stdchecker

std_list = ['D92', 'D93']
actual_std_list = [
    {'id': 1, 'no': 'ASTM D92', 'rev': '18'},
    {'id': 2, 'no': 'ASTM D93', 'rev': '18'}
]

fetch_generator = stdchecker.fetch_astm(std_list)
for i in stdchecker.check_astm(fetch_generator, actual_std_list, id_from_actual=True):
    print(i)
```
Output:
```python
{'query': 'D92',
 'error': None,
 'no': 'ASTM D92',
 'rev': '18',
 'desc': 'Standard Test Method for Flash and Fire Points by Cleveland Open Cup Tester',
 'body': 'astm',
 'url': 'https://www.astm.org/Standards/D92.htm',
 'check': True,
 'actual': '18',
 'id': 1}

{'query': 'D93',
 'error': None,
 'no': 'ASTM D93',
 'rev': '20',
 'desc': 'Standard Test Methods for Flash Point by Pensky-Martens Closed Cup Tester',
 'body': 'astm',
 'url': 'https://www.astm.org/Standards/D93.htm',
 'check': False,
 'actual': '18',
 'id': 2}
```
For more documentation, refer to the docstrings in the source files.

## License
See the [LICENSE](LICENSE) file for license rights and limitations (MIT).
