"""
Payment Gateway implementations for processing song purchases
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List


class PaymentGateway(ABC):
    """Abstract base class for payment gateways"""
    
    @abstractmethod
    def process_payment(self, amount: Decimal, song_ids: List[int]) -> dict:
        """
        Process payment for songs
        
        Args:
            amount: Total amount to charge
            song_ids: List of song IDs being purchased
            
        Returns:
            dict: Transaction response with status, transaction_id, etc.
        """
        pass


class CheapPaymentGateway(PaymentGateway):
    """
    Payment gateway for transactions under $10.
    Simulates a cheap/basic payment processor.
    """
    
    def process_payment(self, amount: Decimal, song_ids: List[int]) -> dict:
        """
        Process payment using the cheap gateway.
        In a real scenario, this would make an API call to the gateway.
        """
        if amount >= Decimal('10.00'):
            raise ValueError("CheapPaymentGateway can only process amounts under $10")
        
        # Simulate payment processing
        return {
            'success': True,
            'gateway': 'CheapPaymentGateway',
            'amount': float(amount),
            'transaction_id': f'CHEAP-{id(object())}-{int(amount * 100)}',
            'status': 'completed',
            'song_ids': song_ids,
            'message': 'Payment processed successfully via CheapPaymentGateway'
        }


class ExpensivePaymentGateway(PaymentGateway):
    """
    Payment gateway for transactions $10 and over.
    Simulates a premium/expensive payment processor with more features.
    """
    
    def process_payment(self, amount: Decimal, song_ids: List[int]) -> dict:
        """
        Process payment using the expensive gateway.
        In a real scenario, this would make an API call to the gateway.
        """
        if amount < Decimal('10.00'):
            raise ValueError("ExpensivePaymentGateway should be used for amounts $10 or over")
        
        # Simulate payment processing with additional features
        return {
            'success': True,
            'gateway': 'ExpensivePaymentGateway',
            'amount': float(amount),
            'transaction_id': f'EXP-{id(object())}-{int(amount * 100)}',
            'status': 'completed',
            'song_ids': song_ids,
            'message': 'Payment processed successfully via ExpensivePaymentGateway',
            'premium_features': True
        }


def get_payment_gateway(amount: Decimal) -> PaymentGateway:
    """
    Factory function to get the appropriate payment gateway based on amount.
    
    Args:
        amount: Total purchase amount
        
    Returns:
        PaymentGateway: The appropriate gateway instance
    """
    if amount >= Decimal('10.00'):
        return ExpensivePaymentGateway()
    else:
        return CheapPaymentGateway()
