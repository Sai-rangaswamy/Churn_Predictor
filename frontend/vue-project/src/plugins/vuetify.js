import "vuetify/styles"
import { createVuetify } from "vuetify"
import * as components from "vuetify/components"
import * as directives from "vuetify/directives"

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'fintech',
    themes: {
      fintech: {
        dark: false,
        colors: {
          primary: '#303F9F',      // indigo-darken-2
          secondary: '#00897B',    // teal-darken-1
          background: '#ECEFF1',   // blue-grey-lighten-5
          surface: '#FFFFFF',
          'on-surface': '#263238', // blue-grey-darken-4
          'on-background': '#263238'
        }
      }
    }
  }
})