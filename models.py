from django.db import models

# Category model to classify spare parts
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# SparePart model to store details about each spare part
class SparePart(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='spare_part_images/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_purchased = models.DateTimeField(null=True, blank=True)  # Add this field

    def __str__(self):
        return self.name
  

    # Custom method to update stock
    def update_stock(self, quantity):
        self.quantity_in_stock += quantity
        self.save()

# Purchase model to record purchases
class Purchase(models.Model):
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate total price before saving
        self.total_price = self.quantity * self.purchase_price
        super(Purchase, self).save(*args, **kwargs)
        # Update stock of the spare part
        self.spare_part.update_stock(self.quantity)


    def __str__(self):
        return f"Purchase of {self.spare_part.name}"


# Sale model to record sales
class Sale(models.Model):
    spare_part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically calculate total price before saving
        self.total_price = self.quantity * self.sale_price
        super(Sale, self).save(*args, **kwargs)
        # Reduce stock of the spare part
        self.spare_part.update_stock(-self.quantity)

    def __str__(self):
        return f"Sale of {self.spare_part.name}"
