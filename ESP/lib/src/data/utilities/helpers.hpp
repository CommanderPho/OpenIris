#include <string>
#include <sstream>
#include <vector>

namespace Helpers
{
    char *itoa(int value, char *result, int base);
    void split(std::string str, std::string splitBy, std::vector<std::string> &tokens);
    std::vector<std::string> split(const std::string &s, char delimiter);
}