conversion
==========

Utility functions to convert strings to Python types.  Currently implements
`convert_bool()`, which will convert truthy strings to `True` and falsey
strings to `False`:

```
>>> from conversion import convert_bool
>>> convert_bool('yes')
True
>>> convert_bool('no')
False
```

When the function does not find the string can be converted, it will return the
value unmodified:

```
>>> convert_bool('yup')
'yup'
```
