
## install

---

Install command:
```
pip install docbook
```

## docbook.conf

---

When you install complete,you should modify the config file: docbook.conf. for example:
```
[qiniu]
bucket_name = test-qn
ACCESS_KEY = ymtUGLMUVsngMcRRZCqnt_m9lOZ5d8pZ1T_KPhA
SECRET_KEY = toOvcxKuL7LcvQdfF646EKGX8Ak4UAR-f3scYMJ

[docbook]
prefix_path = blinq  
input_dir = /home/jeremy/gitbook-zh/
format = site
```

## docbook

---

Use to generate docment and upload to qiniu to read online. for example:

```
docbook

# input_dir is current directory
# output_dir in /tmp/xxx,this directory will be auto delete when the jobs complete.
# format is 'site'

docbook -o xxx

# input_dir is current directory
# output_dir is ./xxx
# format is site

docbook -o /tmp/xxx

# input_dir is current directory
# output_dir is /tmp/xxx
# format is site

docbook -i source_dir -o /tmp/xxx 

# input_dir is input_dir
# output_dir is /tmp/xxx
# format is site

```

## docbook clean

---

Use to batch list/delete files. for example:
```
docbook -b test-qn -a list

# list all files in test-qn

docbook -b test-qn -a list -p test

# list all startwith 'test' files in test-qn

docbook -b test-qn -a delete -p test

# delete all startwith 'test' files
```
