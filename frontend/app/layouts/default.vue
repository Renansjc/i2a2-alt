<template>
  <div class="min-h-screen bg-base-100">
    <div class="navbar bg-base-300">
      <div class="flex-1">
        <NuxtLink to="/" class="btn btn-ghost text-xl">Sistema NF-e</NuxtLink>
      </div>
      <div class="flex-none">
        <ul class="menu menu-horizontal px-1">
          <li><NuxtLink to="/">Visão Geral</NuxtLink></li>
          <li><NuxtLink to="/upload">Upload</NuxtLink></li>
          <li><NuxtLink to="/invoices">Notas Fiscais</NuxtLink></li>
          <li><NuxtLink to="/chat">Chat</NuxtLink></li>
        </ul>
      </div>
    </div>
    <main>
      <slot />
    </main>
    
    <!-- Floating Chat Widget -->
    <FloatingChat />
  </div>
</template>
