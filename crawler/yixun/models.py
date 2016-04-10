from django.db import models

# Create your models here.


class GoodsItem(models.Model):
	cat1 = models.CharField(max_length=40,db_index=True)
	cat2 = models.CharField(max_length=40,db_index=True,null=True)
	cat3 = models.CharField(max_length=40,db_index=True,null=True)
	cat4 = models.CharField(max_length=40,db_index=True,null=True)
	cat5 = models.CharField(max_length=40,db_index=True,null=True)
	brand = models.CharField(max_length=40,db_index=True)
	name = models.CharField(max_length=200,db_index=True)
	price = models.FloatField(default=0)
	url = models.CharField(max_length=200,null=True)
	image = models.BinaryField(null=True)
	image2 = models.BinaryField(null=True)
	image3 = models.BinaryField(null=True)

class GoodsParameter(models.Model):
	item = models.ForeignKey('GoodsItem')
	name = models.CharField(max_length=40)
	value = models.CharField(max_length=120)