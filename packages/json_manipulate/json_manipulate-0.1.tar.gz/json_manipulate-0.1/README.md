# JSON Manipulate

Manipulate JSON strings from the command line.

## Usage

Call the json_manipulate.py with a json-string as standard input and a manipulation string. For example:

```bash
$ json_string='{"first_name" : "Henk", "last_name" : "de Wit", "birth_date" : "1969-03-12"}'
$ echo $json_string | ./json_manipulate.py -m 'first_name'
{
    "first_name": "Henk"
}
```

If you ommit the -m flag, you just get the json-string nicely readable on your screen.

## More examples

Select subkeys:

```bash
$ json_string='{"person" : {"first_name" : "Henk", "last_name" : "de Wit", "birth_date" : "1969-03-12"}}'
$ echo $json_string | ./json_manipulate.py -m 'person.first_name'
{
    "person": {
        "first_name": "Henk"
    }
}
```

Select multiple keys:

```bash
$ json_string='{"person" : {"first_name" : "Henk", "last_name" : "de Wit", "birth_date" : "1969-03-12"}}'
$ echo $json_string | ./json_manipulate.py -m 'person.(first_name|last_name)'
{
    "person": {
        "first_name": "Henk",
        "last_name": "de Wit"
    }
}
```

Select keys from objects inside a list:

```bash
$ json_string='{"persons" : [{"first_name" : "Henk", "last_name" : "de Wit", "birth_date" : "1969-03-12"}, {"first_name" : "Karin", "last_name" : "de Wit", "birth_date" : "1970-11-05"}]}'
$ echo $json_string | ./json_manipulate.py -m 'persons[first_name|last_name]'
{
    "persons": [
        {
            "first_name": "Henk",
            "last_name": "de Wit"
        },
        {
            "first_name": "Karin",
            "last_name": "de Wit"
        }
    ]
}

```