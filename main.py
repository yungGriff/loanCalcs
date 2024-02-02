import pandas as pd
import random

class Loan:
    def __init__(self, balance, interest_rate, min_payment):
        self.balance = balance
        self.interest_rate = interest_rate
        self.min_payment = min_payment

# Function to calculate total interest paid
def calculate_total_interest_paid(loans, loan_term_years=10):
    total_interest_paid = 0
    for _, loan in loans.iterrows():
        remaining_balance = loan['balance']
        for _ in range(loan_term_years * 12):
            interest_payment = remaining_balance * loan['interest_rate'] / 12
            total_interest_paid += interest_payment
            remaining_balance -= min(loan['min_payment'], remaining_balance + interest_payment)

    return total_interest_paid

# Function to calculate projected interest over the entire loan term
def calculate_projected_interest(loans, loan_term_years=10):
    projected_interest = []
    for _, loan in loans.iterrows():
        remaining_balance = loan['balance']
        interest_for_loan = 0
        for _ in range(loan_term_years * 12):
            interest_payment = remaining_balance * loan['interest_rate'] / 12
            interest_for_loan += interest_payment
            remaining_balance -= min(loan['min_payment'], remaining_balance + interest_payment)
        projected_interest.append((loan.name + 1, interest_for_loan))
    return projected_interest

# Function to make payments using the snowball method
def snowball_payment(loans, extra_payment, loan_term_years=10):
    total_interest_with_min_payment = calculate_total_interest_paid(loans.copy(), loan_term_years)
    paid_off_loans = []

    while loans['balance'].sum() > 0:
        min_payment_loans = loans[loans['min_payment'] > 0]
        if min_payment_loans.empty:
            break  # Exit if all loans are paid off

        loan_num = min_payment_loans['balance'].idxmin() + 1
        loan = loans.loc[loan_num - 1]
        interest_payment = loan['balance'] * loan['interest_rate'] / 12
        principal_payment = min(loan['min_payment'] + extra_payment, loan['balance'] + interest_payment)

        loans.loc[loan_num - 1, 'balance'] -= principal_payment
        loans.loc[loan_num - 1, 'min_payment'] = 0  # No additional minimum payment for fully paid loan
        paid_off_loans.append((loan_num, extra_payment))

    total_interest_with_method = calculate_total_interest_paid(loans, loan_term_years)
    years_early = loan_term_years - (total_interest_with_method / total_interest_with_min_payment)  # Calculate years early
    return total_interest_with_min_payment - total_interest_with_method, paid_off_loans, years_early

# Function to make payments using the avalanche method
def avalanche_payment(loans, extra_payment, loan_term_years=10):
    sorted_loans = loans.sort_values(by=['interest_rate', 'balance'], ascending=[True, True])
    return snowball_payment(sorted_loans, extra_payment, loan_term_years)

# Function to make payments using the fine-tuned hybrid method
def fine_tuned_hybrid_payment(loans, extra_payment, loan_term_years=10):
    total_interest_with_min_payment = calculate_total_interest_paid(loans.copy(), loan_term_years)
    projected_interest = calculate_projected_interest(loans, loan_term_years)
    prioritized_loans = sorted(projected_interest, key=lambda x: x[1], reverse=True)
    paid_off_loans = []

    while loans['balance'].sum() > 0 and prioritized_loans:
        loan_num, _ = prioritized_loans.pop(0)
        loan = loans.loc[loan_num - 1]
        interest_payment = loan['balance'] * loan['interest_rate'] / 12
        principal_payment = min(loan['min_payment'] + extra_payment, loan['balance'] + interest_payment)

        loans.loc[loan_num - 1, 'balance'] -= principal_payment
        loans.loc[loan_num - 1, 'min_payment'] = 0  # No additional minimum payment for fully paid loan
        paid_off_loans.append((loan_num, extra_payment))

    total_interest_with_method = calculate_total_interest_paid(loans, loan_term_years)
    years_early = loan_term_years - (total_interest_with_method / total_interest_with_min_payment)  # Calculate years early
    return total_interest_with_min_payment - total_interest_with_method, paid_off_loans, years_early

# Function to generate test loans
def generate_test_loans(num_loans):
    loans = []
    for i in range(1, num_loans + 1):
        balance = random.randint(5000, 10000)
        interest_rate = round(random.uniform(0.02, 0.1), 4)
        min_payment = round(balance * interest_rate, 2)
        loans.append(Loan(balance, interest_rate, min_payment))
    return loans

# Example usage:
loan_data = {
    'balance': [3560, 3282, 5489, 7038, 5460, 7042],
    'interest_rate': [0.0453, 0.0275, 0.0373, 0.0373, 0.0499, 0.0499],
    'min_payment': [37, 31, 55, 70, 58, 75]
}

loans_df = pd.DataFrame(loan_data)
loans_df.index.name = 'Loan'
#$174
extra_payment = 174  # Only the extra payment amount

# Snowball method
snowball_savings, snowball_order, snowball_years_early = snowball_payment(loans_df.copy(), extra_payment)
print(f"Savings with snowball method: ${-snowball_savings:.2f}")
print(f"Order of loans paid off with snowball method: {snowball_order}")
print(f"Years early with snowball method: {snowball_years_early:.2f} years")

# Avalanche method
avalanche_savings, avalanche_order, avalanche_years_early = avalanche_payment(loans_df.copy(), extra_payment)
print(f"Savings with avalanche method: ${-avalanche_savings:.2f}")
print(f"Order of loans paid off with avalanche method: {avalanche_order}")
print(f"Years early with avalanche method: {avalanche_years_early:.2f} years")

# Fine-tuned Hybrid method
hybrid_savings, hybrid_order, hybrid_years_early = fine_tuned_hybrid_payment(loans_df.copy(), extra_payment)
print(f"Savings with hybrid method: ${-hybrid_savings:.2f}")
print(f"Order of loans paid off with hybrid method: {hybrid_order}")
print(f"Years early with hybrid method: {hybrid_years_early:.2f} years")

# Test Snowball method
test_loans_data = {
    'balance': [5000, 7000, 3000, 10000, 8000],
    'interest_rate': [0.03, 0.05, 0.1, 0.07, 0.04],
    'min_payment': [50, 70, 30, 100, 80]
}

test_loans_df = pd.DataFrame(test_loans_data)
test_loans_df.index.name = 'Loan'
test_snowball_savings, _, _ = snowball_payment(test_loans_df.copy(), extra_payment)
print(f"Test Savings with snowball method: ${-test_snowball_savings:.2f}")

# Test Avalanche method
test_avalanche_savings, _, _ = avalanche_payment(test_loans_df.copy(), extra_payment)
print(f"Test Savings with avalanche method: ${-test_avalanche_savings:.2f}")

# Test Fine-tuned Hybrid method
test_hybrid_savings, _, _ = fine_tuned_hybrid_payment(test_loans_df.copy(), extra_payment)
print(f"Test Savings with hybrid method: ${-test_hybrid_savings:.2f}")
