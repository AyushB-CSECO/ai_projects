def calculator(a: int, b: int  ) -> str: 
    sum_val, diff_val = a+b, a-b
    mul_val, div_val = a*b, a/b

    return f"""
    {a} + {b} = {sum_val}
    {a} - {b} = {diff_val}
    {a} x {b} = {mul_val}
    {a} / {b} = {div_val}
    """
