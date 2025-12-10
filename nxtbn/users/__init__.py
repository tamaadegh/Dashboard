from django.db import models


class UserRole(models.TextChoices):
    """
    Defines the various user roles within the application, each tailored to specific responsibilities 
    and permissions. These roles ensure a clear separation of duties and proper access control.

    Roles:
    - CUSTOMER: Represents an end-user who purchases products or services.
    - ADMIN: Represents an administrative user with full control over the platform.
    - STORE_MANAGER: Manages daily store operations, including orders and inventory.
    - PRODUCT_MANAGER: Oversees product listings and inventory details.
    - MARKETING_MANAGER: Focuses on campaigns, promotions, and customer engagement.
    - ORDER_PROCESSOR: Handles order processing and fulfillment.
    - CUSTOMER_SUPPORT_AGENT: Provides assistance to customers and resolves inquiries.
    - ACCOUNTANT: Manages financial data, including reports, invoices, and taxes.
    - VENDOR: Manages their own product listings and orders (for multi-vendor setups).
    """

    CUSTOMER = 'CUSTOMER', 'Customer'
    """
    Customer:
    - Description: End-user who interacts with the application to browse, purchase, and manage orders.
    - Permissions:
      - View product listings.
      - Place orders and track order status.
      - Manage their own account details (e.g., profile, password).
      - Leave product reviews.
    - Restrictions:
      - Cannot access administrative or management features.
    """

    ADMIN = 'ADMIN', 'Admin'
    """
    Admin:
    - Description: Has the highest level of control over the application.
    - Permissions:
      - Manage all aspects of the platform, including settings, users, and roles.
      - Access all data (e.g., products, orders, users, analytics).
      - Install, update, and remove plugins or system extensions.
      - Configure platform-wide settings (e.g., tax, currency, and language options).
    - Restrictions:
      - None.
    """

    STORE_MANAGER = 'STORE_MANAGER', 'Store Manager'
    """
    Store Manager:
    - Description: Oversees the day-to-day operations of the store.
    - Permissions:
      - Add, edit, and delete product listings and categories.
      - Manage orders, including processing, refunds, and cancellations.
      - Oversee inventory and stock levels.
      - Access sales analytics and reporting tools.
      - Including all permissions of Product Manager
      - Including all permissions of Order Processor
      - Including all permissions of Marketing Manager
      - Including all permissions of Accountant
      - Including all permissions of Vendor
      - Including all permissions of Customer Support Agent
    - Restrictions:
      - Cannot modify system-level settings or manage users/roles.
    """

    PRODUCT_MANAGER = 'PRODUCT_MANAGER', 'Product Manager'
    """
    Product Manager:
    - Description: Responsible for managing product listings and related details.
    - Permissions:
      - Add, edit, and update product information (e.g., titles, descriptions, prices).
      - Manage product categories, tags, and attributes.
      - Track inventory levels and adjust stock as needed.
    - Restrictions:
      - Cannot manage orders or customer accounts.
      - Cannot delete products unless explicitly permitted.
    """

    MARKETING_MANAGER = 'MARKETING_MANAGER', 'Marketing Manager'
    """
    Marketing Manager:
    - Description: Focuses on driving customer engagement through campaigns and promotions.
    - Permissions:
      - Create and manage discount codes, coupons, and gift cards.
      - Set up and manage marketing campaigns (e.g., email newsletters).
      - Access analytics for campaign performance metrics.
    - Restrictions:
      - Cannot manage orders, products, or customers directly.
      - Limited access to financial reports and sensitive data.
    """

    ORDER_PROCESSOR = 'ORDER_PROCESSOR', 'Order Processor'
    """
    Order Processor:
    - Description: Manages the order fulfillment process.
    - Permissions:
      - Update order statuses (e.g., pending, processing, shipped).
      - Generate and print shipping labels or invoices.
      - Notify customers about order updates.
    - Restrictions:
      - Cannot edit or cancel orders without approval.
      - Cannot manage products, customer data, or analytics.
    """

    CUSTOMER_SUPPORT_AGENT = 'CUSTOMER_SUPPORT_AGENT', 'Customer Support Agent'
    """
    Customer Support Agent:
    - Description: Provides assistance to customers and resolves their inquiries.
    - Permissions:
      - View orders and customer details for support purposes.
      - Respond to customer inquiries and manage support tickets.
      - Issue refunds with appropriate approvals.
    - Restrictions:
      - Cannot manage products, inventory, or orders directly.
      - Limited access to financial and sales data.
    """

    ACCOUNTANT = 'ACCOUNTANT', 'Accountant'
    """
    Accountant:
    - Description: Manages the financial aspects of the platform.
    - Permissions:
      - Access financial reports and sales data.
      - Generate invoices and handle tax calculations.
      - Process refunds and manage payouts to vendors.
    - Restrictions:
      - Cannot manage products, customers, or site-level settings.
    """

    VENDOR = 'VENDOR', 'Vendor'
    """
    Vendor:
    - Description: Manages their own products and orders in a multi-vendor setup.
    - Permissions:
      - Add, edit, and delete their own product listings.
      - Manage orders related to their own products.
      - View sales data for their own products.
    - Restrictions:
      - No access to other vendors' data or orders.
    """
    

    STORE_VIEWER = 'STORE_VIEWER', 'Store Viewer'
    """
    Store Viewer:
    - Description: Has read-only access to the entire store.
    - Permissions:
      - View all product listings and categories.
      - View all orders and customer details.
      - Access sales analytics and reporting tools.
    - Restrictions:
      - Cannot add, edit, or delete any data.
      - Cannot manage users, roles, or system settings.
    """

    TRANSLATOR = 'TRANSLATOR', 'Translator'
    """
    Translator:
    - Description: Responsible for translating content into different languages.
    - Permissions:
      - Translate product listings, categories, and other site content.
      - Manage translations for various languages.
    """

    PROCUREMENT_MANAGER = 'PROCUREMENT_MANAGER', 'Procurement Manager'
    """
    Procurement Manager:
    - Description: Manages the procurement process for sourcing products.
    - Permissions:
      - Create and manage purchase orders for product procurement.
      - Track supplier information and manage relationships.
      - Monitor inventory levels and stock availability.
    """