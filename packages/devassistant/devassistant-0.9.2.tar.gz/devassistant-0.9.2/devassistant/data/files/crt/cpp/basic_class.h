#ifndef BASIC_CLASS_H
#define BASIC_CLASS_H

#include <string>

class BankAccount
{
    public:
        BankAccount(std::string, std::string, long);
        ~BankAccount();
        std::string GetName() const { return name; }
        std::string GetCurrency() const { return currency; }
        long GetDeposit() const { return deposit; }
        void SetName(std::string bankName) { name = bankName; }
        void SetCurrency(std::string bankCurrency) { currency = bankCurrency; }
        void SetDeposit(long bankDeposit) { deposit = bankDeposit; }

    private:
        std::string name;
        std::string currency;
        long deposit;
};

#endif
