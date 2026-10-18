#include <cassert>
#include <cstring>
#include <netdb.h>
#include <arpa/inet.h>
#include "nsl.hpp"

int main() {
  hostent* h = my_gethostbyname_r("localhost", AF_INET);
  assert(h && h->h_addrtype == AF_INET && h->h_length == 4);
  unsigned char address[4];
  memcpy(address, h->h_addr_list[0], 4);
  volatile char stack[8192];
  for (unsigned i=0; i<sizeof(stack); ++i) stack[i] = 'x';
  assert(!memcmp(address, h->h_addr_list[0], 4));
  my_free_hostent(h); // libc/thread-local hostent storage must not be freed.
  h = my_gethostbyname("localhost", AF_INET);
  assert(h && h->h_addrtype == AF_INET);
  my_free_hostent(h);
  in_addr ip;
  assert(inet_pton(AF_INET, "127.0.0.1", &ip) == 1);
  const char* text = my_inet_ntop(AF_INET, &ip);
  assert(text && !strcmp(text, "127.0.0.1"));
}
