from store.models import Product, Profile

class Cart():
    def __init__(self, request):
        self.session = request.session
        self.request = request
        cart = self.session.get('session_key')
        
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}
        
        self.cart = cart
    
    def __len__(self):
        return len(self.cart)
    
    def persist_add(self, product, quantity):
        product_id = str(product)
        quantity = int(quantity)
        if product_id in self.cart:
            self.cart = self.update(product_id, quantity)
        else:
            self.cart[product_id] = int(quantity)
        self.session.modified = True
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_format = str(self.cart).replace("'",'"')
            current_user.update(old_cart=str(cart_format))
    
    def add(self, product, quantity):
        product_id = str(product.id)
        quantity = int(quantity)
        if product_id in self.cart:
            self.cart = self.update(product_id, quantity)
        else:
            self.cart[product_id] = int(quantity)
        self.session.modified = True
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_format = str(self.cart).replace("'",'"')
            current_user.update(old_cart=str(cart_format))
            
        
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        current_cart = self.cart
        current_cart[product_id] = product_qty
        self.session.modified = True
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_format = str(self.cart).replace("'",'"')
            current_user.update(old_cart=str(cart_format))
        return self.cart
    
    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True
        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            cart_format = str(self.cart).replace("'",'"')
            current_user.update(old_cart=str(cart_format))
        return self.cart
    
    def get_cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart
        total = 0
        for key, val in cart.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total += (val*product.sale_price)
                    else:
                        total += (val*product.price)                    
        return total
        
    def get_products(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        return products
    
    def get_quantities(self):
        quantities = self.cart
        return quantities