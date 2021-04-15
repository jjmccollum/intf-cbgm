<template>
  <div class="vm-index">
    <div class="container bs-docs-container">
      <div v-if="$store.getters.can_read">
        <router-link
          class="biglink"
          :to="{ name: 'coherence', params: { passage_or_id: 1 } }"
          >Coherence and Textual Flow</router-link
        >
        <router-link class="biglink" :to="{ name: 'comparison' }"
          >Comparison of Witnesses</router-link
        >
        <router-link class="biglink" :to="{ name: 'find_relatives' }"
          >Find Relatives</router-link
        >
        <div v-if="$store.getters.can_read_private">
          <router-link class="biglink" :to="{ name: 'notes_list' }"
            >List of Notes</router-link
          >
          <router-link class="biglink" :to="{ name: 'opt_stemma' }"
            >Optimal Substemma</router-link
          >
          <router-link class="biglink" :to="{ name: 'set_cover' }"
            >Minimum Set Cover</router-link
          >
        </div>
      </div>

      <a class="biglink" href="/pdfs/GenQ4_Guide.pdf" target="_blank"
        >Short Guide (PDF)</a
      >
    </div>
  </div>
</template>

<style lang="scss">
/* index.vue */

div.vm-index {
  a.biglink {
    display: block;
    font-size: 150%;
    margin: 1em 0;
  }

  div.gdpr {
    margin-top: 1em;
  }
}
</style>
