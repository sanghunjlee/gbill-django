# gBill

*an app for splitting bills amongst other people*

---

## Getting Started

### Install required packages

```bash
pip install -r requirement.txt
```

### Set up the `SECRET_KEY`

First, create a `.env` file in the root directory (same level as the `manage.py`)

Access the Python interactive shell by running the following in the terminal

```bash
(env) $ python manage.py shell
```

In the shell, import the `get_random_secret_key()` function from `django.core.management.utils`

```python
>>> from django.core.management.utils import get_random_secret_key
```

Use the function to generate the secret key

```python
>>> get_random_secret_key()
somerandomkeygenerated
```

Copy this secret key and set it as `SECRET_KEY` value in the `.env` file

```env
SECRET_KEY='somerandomkeygenerated'
```

### Start the development server

Now you can run the development server by running the following

```bash
(env) $ python manage.py runserver
```

Optionally you can provide a specific port

```bash
(env) $ python manage.py runserver 8000
```

### Open the `/gbill` app

Access the app by going to the `/gbill` page of the server. (e.g. http://localhost:8000/gbill)

---

## Project Description

This is an app designed to split bills amongst other people by using the **minimal** number of transactions. 

<details>
<summary>Brief Explanation</summary>
When we have multiple people who paid for multiple different transactions, it gets difficult to calculate who owes how much to whom. Simple way to calculate is to sum up everything person A owes to person B. But this creates multiple extraneous transaction. For example, after summing up the debt we have:

**Method 1**
* **`A`** pays **10** to **`B`**
* **`B`** pays **40** to **`C`**
* **`C`** pays **20** to **`A`** 

```mermaid
flowchart LR
n1([A]) --> |pays 10| n2([B])
n2([B]) --> |pays 40| n3([C])
n3([C]) --> |pays 20| n1([A]) 
```

This required 3 transactions to settle the debts. Now instead, we can have `B` pays for `A` by not accepting the payment from `A`:

**Method 2**
* **`B`** pays **10** to **`A`**
* **`B`** pays **20** to **`C`**

```mermaid
flowchart LR
n2([B]) --> |pays 10| n1([A])
n2([B]) --> |pays 20| n3([C])
```

This new method required 2 transactions to settle the debts. And to double check, we can check how much money each person have in the end for each method:

| **Method 1**                      | **Method 2**                        |
|-----------------------------------|-------------------------------------|
| **`A`** has (-10) + (20) = **10** | **`A`** has **10**                  |
| **`B`** has 10 + (-40) = **-30**  | **`B`** has (-10) + (-20) = **-30** |
| **`C`** has 40 + (-20) = **20**   | **`C`** has **20**                  |

And thus, we conclude there is no discrepancy for method 2 despite at a glance it looks wrong.
</details>

---

## Note

---

## To-Do's
- [ ] CLI Feature
- [x] Convert tkinter gui to django
- [ ] Export result as PDF, PNG, and TXT
- [ ] Implement more graphs to show accounting data
- [ ] Implement users & saving/loading & sharing bill info

<details>
<Summary>Trashed ideas</summary>

    - Implement Docker
    - Convert to Flask (instead of Django)


</details>
