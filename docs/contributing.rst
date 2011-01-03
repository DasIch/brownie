.. _contributing:

Contributing
============
If you want to contribute to Brownie there are a couple of simple basic
rules which you should follow:

1. Unless your change requires just one commit open a branch for it.
   
   If you are forking on Github_ and do not want to have any weird merging
   issues in the future I recommend creating branches for every feature
   unless you are sure it is going to be pulled.

2. Tests and documentation are just as important as the implementation
   itself, so before making a commit...
   
   - ...check if everything is tested.
   - ...check if everything is documented, this includes a mention in the
     change log.
   - ...run ``make test``.

3. If this is your first contribution add yourself to the list of
   :ref:`authors`, please.

4. When you make a pull request:
  
   - Explain in one or two sentences what it is about.
   - Mention the use cases unless it is a bugfix, if you can only think of
     one that is fine, too.

   As a general rule I should not have to read your code at all to know
   what it is about.

.. _Github: http://github.com/
