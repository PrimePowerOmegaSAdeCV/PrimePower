# Reporte de ventas:
<<<<<<< HEAD

=======
Reporte de infomre_fabricacion de empaques modificado
>>>>>>> master
```python
orden_compra AS(
SELECT purchase.name as purchase_name,purchase.id as remision,sale_order_line.id as line_id   FROM sale_order_line
  LEFT JOIN purchase_order as purchase ON sale_order_line.nombre_orden_id=purchase.origin ORDER BY purchase.name ASC)
```
| purchase_name | remision | line_id |
|---------------|----------|---------|
| P00009        | 9        | 36      |
| P00010        | 10       | 36      |
| P00010        | 10       | 35      |
```python
(SELECT string_agg(purchase_name, ',') FROM orden_compra oc WHERE oc.line_id = sale_order_line.id)
        AS partner_ref,
```
Concatena la columna en donde se cumpla la codicion

| purchase_name | 
|---------------|
| P00009        | 
| P00010        | 
| P00010        | 

se pasa a 

| partner_ref | 
|---------------|
| P00009, P00010| 
