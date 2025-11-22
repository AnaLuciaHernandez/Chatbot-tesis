from typing import Any, Text, Dict, List
import re

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionClasificarViolenciaMixta(Action):
    """
    Clasifica tipos de violencia de género basándose en patrones de lenguaje
    frecuentes en relatos en español (Argentina) y devuelve un mensaje empático.
    Puede detectar varios tipos de violencia al mismo tiempo.
    """

    # Orden en el que queremos mostrar los tipos
    ORDEN_TIPOS = ["física", "psicológica", "sexual", "económica", "simbólica", "institucional"]

    NOMBRES_TIPOS: Dict[Text, Text] = {
        "física": "violencia física",
        "psicológica": "violencia psicológica o emocional",
        "sexual": "violencia sexual",
        "económica": "violencia económica o patrimonial",
        "simbólica": "violencia simbólica",
        "institucional": "violencia institucional",
    }

    # Patrones de detección por tipo
    TIPOS_VIOLENCIA: Dict[Text, List[Text]] = {
        "física": [

            # golpes en general
            r"\bme\s+(pega|pegó|pego|golpea|golpeó|golpeo|caga\s+a\s+palos)\b",

            # empujones
            r"\bme\s+(empuja|empujó|empujo|empuj[aó])\b",
            r"\bme\s+empuja\s+fuerte\b",

            # tirar del pelo
            r"\bme\s+(tiró|tira|tir[oó])\s+del\s+pelo\b",

            # sacudidas / zamarreos
            r"\bme\s+(zamarrea|zamarreó|sacude|sacudió|sacudi[oó])\b",

            # cachetadas / patadas
            r"\bme\s+cachete(ó|a)\b",
            r"\bme\s+pate(ó|a)\b",

            # estrangular / ahorcar
            r"\bme\s+(estrangula|ahorca|ahorc[oó])\b",

            # morder
            r"\bme\s+mordi(ó|e)\b",

            # arrastrar / encerrar / quemar
            r"\bme\s+arrastr(ó|a)\b",
            r"\bme\s+encerr(ó|a)\b",
            r"\bme\s+quem(ó|a)\b",

            # tirar cosas / romper cosas
            r"\bme\s+tir(a|ó)\s+cosas\b",
            r"\bme\s+tir[oó]\s+cosas\b",
            r"\bme\s+rompi(ó|e)\s+algo\b",

            # agarrar / apretar brazos
            r"\bme\s+agarr(a|ó).*(del|de\s+los)\s+brazo[s]?\b",
            r"\bme\s+aprieta.*brazo[s]?\b",
            r"\bme\s+agarr(a|ó)\s+fuerte\b",
            r"\bme\s+agarr(a|ó)\s+del\s+brazo\b",

            # empujar contra algo
            r"\bme\s+empuja\s+contra\s+la\s+pared\b",
            r"\bme\s+empuj[oó]\s+contra\s+la\s+pared\b",
            r"\bme\s+empuja\s+en\s+la\s+cama\b",
            r"\bme\s+empuj[oó]\s+en\s+la\s+cama\b",
            # moretones / marcas
            r"\bme\s+dej[óo]\s+moretones\b",
            r"\bme\s+dej[óo]\s+marcas\b",
            r"\btengo\s+moretones\b",
            r"\bmoretones\b",
            r"\bmoret[oó]n\b",

            # NUEVOS PATRONES AGREGADOS
            r"\bme\s+peg[óo]\s+con\b",
            r"\bme\s+dej[óo]\s+moretones\b",
            r"\bme\s+dej[óo]\s+marcas\b",
            r"\btengo\s+moretones\b",
        ],

        "psicológica": [
            # Insultos directos
            r"\bme\s+insulta\b",
            r"\bme\s+insult[óo]\b",
            r"\bme\s+viv[eí]s?\s+insultando\b",
            r"\bme\s+dice\s+(puta|idiota|inútil|loca|estúpida|tarada|imbécil|mierda)\b",
            r"\bme\s+trat(a|ó)\s+de\s+(puta|idiota|inútil|loca|estúpida|tarada|imbécil|mierda)\b",
            r"\bme\s+insulta\b",
            r"\bme\s+insulta\s+todo\s+el\s+tiempo\b",
            r"\bme\s+vive\s+insultando\b",
            r"\bme\s+insulta\s+cuando\s+se\s+enoja\b",
            r"\binsulta\b",
            r"\binsulta\s+todo\s+el\s+tiempo\b",
            r"\bme\s+trata\s+mal\b",
            r"\bme\s+habla\s+mal\b",
            r"\bme\s+grita\b",
            r"\bme\s+grita\s+todo\s+el\s+tiempo\b",

            # Maltrato verbal más general
            r"\bme\s+grita\b",
            r"\bme\s+grit[óo]\b",
            r"\bme\s+habla\s+mal\b",
            r"\bme\s+denigra\b",
            r"\bme\s+humilla\b",

            # Gaslighting / minimizar / culpar
            r"\bme\s+dice\s+que\s+exagero\b",
            r"\bme\s+dice\s+que\s+estoy\s+loca\b",
            r"\bme\s+hace\s+sentir\s+culpable\b",
            r"\b(es|soy)\s+una\s+exagerada\b",
            r"\bme\s+dice\s+que\s+exagero\s+todo\b",
            r"\bme\s+culpa\s+de\s+todo\b",

            # Amenazas emocionales
            r"\bsi\s+me\s+dej(as|ás).*(mato|hago\s+algo)\b",
            r"\bme\s+amenaza\b",
            r"\bamenaza\s+con\s+ir(se)?\b",

            # Control / manipulación emocional
            r"\bme\s+manipula\b",
            r"\bme\s+manipul[oó]\b",
            # Quitar el celular / sacar el celular / quitar el teléfono
            r"\bme\s+quita\s+el\s+celular\b",
            r"\bme\s+saca\s+el\s+celular\b",
            r"\bme\s+agarra\s+el\s+celular\b",

            # Frases de desvalorización afectiva
            r"\bme\s+dice\s+que\s+nadie\s+m[aá]s\s+me\s+va\s+a\s+querer\b",
            r"\bdice\s+que\s+nadie\s+m[aá]s\s+me\s+va\s+a\s+querer\b",

            # Comparaciones constantes
            r"\bme\s+compara\s+todo\s+el\s+tiempo\s+con\s+su\s+ex\b",
            r"\bme\s+compara\s+con\s+su\s+ex\b",

            # Silencio como castigo
            r"\bme\s+deja\s+de\s+hablar\s+por\s+d[ií]as\b",
            r"\bme\s+deja\s+de\s+hablar\b",

            # Gaslighting sin el "me dice"
            r"\bdice\s+que\s+estoy\s+loca\b",
            r"\bdice\s+que\s+me\s+lo\s+invento\s+todo\b",

            # Celos / control social y aislamiento
            r"\bme\s+controla\s+(el\s+celular|el\s+telefono|el\s+teléfono|las\s+redes)\b",
            r"\bcontrola\s+(mi\s+celular|mis\s+redes)\b",
            r"\brevisa\s+mi\s+celular\b",
            r"\brevisa\s+mis\s+mensajes\b",
            r"\bno\s+me\s+deja\s+ver\s+a\s+mi\s+familia\b",
            r"\bno\s+me\s+deja\s+tener\s+amig[oa]s\b",
            r"\bme\s+aisla\b",
            r"\bme\s+aleja\s+de\s+mi\s+familia\b",
            r"\bcelos?\s+enfermiz[oa]s?\b",
            r"\bme\s+cela\s+por\s+todo\b",
            # PARCHE insultos variantes
            r"\bme\s+dice\s+que\s+no\s+sirvo\b",
            r"\bme\s+trata\s+de\s+in[uú]til\b",
            r"\bsos\s+una\s+in[uú]til\b",
            r"\bme\s+trata\s+de\s+idiota\b",
            r"\bme\s+trata\s+de\s+est[uú]pida\b",

            # Humillación / burla
            r"\bse\s+burla\s+de\s+m[ií]\b",
            r"\bme\s+imita\s+delante\s+de\s+otros\b",

            # NUEVOS PATRONES AGREGADOS
            r"\bme\s+dice\s+cosas\s+feas\b",
            r"\bme\s+compara\s+con\s+otras?\b",
            r"\bdice\s+que\s+no\s+sirvo\b",
            r"\bme\s+humilla\s+(en\s+p[uú]blico|delante\s+de)\b",
            r"\bme\s+hace\s+sentir\s+(mal|in[uú]til|menos)\b",
            r"\bme\s+dice\s+que\s+sin\s+[ée]l\s+no\s+soy\s+nada\b",
            # "sin él no soy/sería nada"
            r"\bsin\s+[ée]l\s+(no\s+)?(soy|ser[ií]a)\s+nada\b",
            r"\bdice\s+que\s+sin\s+[ée]l\s+(no\s+)?(soy|ser[ií]a)\s+nada\b",
            r"\bno\s+me\s+deja\s+ir\s+(sola\s+)?a\s+ver\s+a\s+mi\s+familia\b",


        ],

        "sexual": [
            r"\bme\s+oblig[ao].*tener\s+relaciones\b",
            r"\bme\s+forz[ao].*tener\s+sexo\b",
            r"\bme\s+presiona\s+para\s+tener\s+sexo\b",
            r"\bno\s+respeta\s+cuando\s+digo\s+no\b",
            r"\bno\s+qu[ií]a\s+pero\s+igual\s+lo\s+hizo\b",
            r"\bme\s+toc[ao]\s+sin\s+permiso\b",
            r"\bme\s+manosea\b",
            r"\bme\s+bes[ao]\s+a\s+la\s+fuerza\b",
            r"\bme\s+hizo\s+cosas\s+mientras\s+yo\s+dorm[ií]a\b",
            r"\bme\s+lastima\s+durante\s+el\s+sexo\b",
            r"\babusa\s+sexualmente\s+de\s+m[ií]\b",
            r"\bme\s+viola\b",
            r"\bme\s+obliga\s+a\s+ver\s+pornograf[ií]a\b",
            r"\bme\s+graba\s+sin\s+permiso\b",
            r"\bme\s+saca\s+fotos\s+sin\s+que\s+yo\s+quiera\b",
            r"\bme\s+oblig[ao].*tener\s+sexo\b"
            # PARCHES NUEVOS
            r"\bme\s+presiona\s+para\s+tener\s+relaciones\b",
            r"\bme\s+oblig[ao]\s+a\s+tener\s+relaciones\b",
            r"\bsi\s+no\s+tengo\s+relaciones\b",
            r"\bsi\s+no\s+quiero\s+tener\s+relaciones\b",
            r"\bsi\s+no\s+lo\s+hago.*me\s+va\s+a\s+sacar\s+la\s+tarjeta\b",
            r"\bsi\s+no\s+lo\s+hago.*no\s+me\s+va\s+a\s+dar\s+plata\b",
          
            # Presión hasta que cede
            r"\binsiste\s+hasta\s+que\s+cedo\b",
            r"\bme\s+insiste\s+hasta\s+que\s+cedo\b",

            # Tocamientos mientras duerme
            r"\bme\s+toca\s+cuando\s+estoy\s+dormid[ao]\b",
            r"\bme\s+hace\s+cosas\s+mientras\s+duermo\b",

            # No respeta el NO
            r"\bno\s+respeta\s+cuando\s+digo\s+que\s+no\b",
            r"\bno\s+respeta\s+mi\s+no\b",

            # Obligación de prácticas sexuales
            r"\bme\s+obliga\s+a\s+hacer\s+cosas\s+sexuales\s+que\s+no\s+quiero\b",
            r"\bme\s+obliga\s+a\s+hacer\s+cosa[s]?\s+que\s+no\s+quiero\s+en\s+la\s+cama\b",

            # "Relaciones" como sinónimo de sexo
            r"\bme\s+presiona\s+para\s+tener\s+relaciones\b",
            r"\bme\s+obliga\s+a\s+tener\s+relaciones\b",
            r"\bsi\s+no\s+quiero\s+tener\s+relaciones\b",
        ],

        "económica": [
            r"\bse\s+queda\s+con\s+todo\s+lo\s+que\s+gano\b",
            r"\bse\s+queda\s+con\s+todo\s+lo\s+que\s+yo\s+gano\b",
            r"\bse\s+queda\s+con\s+lo\s+que\s+gano\b",

            r"\bme\s+retiene\s+la\s+(plata|tarjeta|pensión|asignación)\b",
            r"\bme\s+retiene\s+todo\s+el\s+dinero\b",

            r"\bme\s+pide\s+cuentas\s+de\s+cada\s+peso\b",
            r"\bme\s+pide\s+cuentas\s+de\s+toda\s+la\s+plata\b",
            r"\bme\s+pide\s+cuentas\s+del\s+dinero\b",
            # PARCHE SUPER DETALLADO PARA ECONÓMICA (NO BORRAR)
            r"\bme\s+retiene\s+(la\s+)?(tarjeta|plata|dinero|sueldo|pensión|asignación)\b",
            r"\bme\s+quita\s+(la\s+)?(tarjeta|plata|dinero|sueldo|pensión|asignación)\b",
            r"\bme\s+saca\s+(la\s+)?(tarjeta|plata|dinero|sueldo|pensión|asignación)\b",
            r"\bse\s+queda\s+con\s+(mi\s+)?(tarjeta|plata|dinero|sueldo|pensión|asignación)\b",
            r"\bmaneja\s+tod[ao]\s+mi\s+(dinero|plata|sueldo)\b",

            # Variantes sin “me”
            r"\bretiene\s+(mi\s+)?(tarjeta|plata|dinero|sueldo|pensión|asignación)\b",
            r"\bquita\s+(mi\s+)?(tarjeta|plata|dinero|sueldo|pensión|asignación)\b",
            r"\bsaca\s+(mi\s+)?(tarjeta|plata|dinero|sueldo|pensión|asignación)\b",

            # Control financiero fuerte
            r"\bcontrola\s+todo\s+mi\s+(dinero|plata|sueldo)\b",
            r"\bmaneja\s+todo\s+mi\s+(dinero|plata|sueldo)\b",
            r"\bno\s+puedo\s+usar\s+mi\s+(dinero|plata|sueldo)\b",

            # Pensiones
            r"\bno\s+me\s+da\s+mi\s+pensi[oó]n\b",
            r"\bno\s+me\s+da\s+mi\s+asignación\b",
            r"\bse\s+queda\s+con\s+mi\s+asignación\b",

            # Control por dependencia económica
            r"\bme\s+deja\s+sin\s+plata\b",
            r"\bme\s+deja\s+sin\s+dinero\b",
            r"\bme\s+deja\s+sin\s+comida\b",
            r"\bno\s+me\s+da\s+plata\b",
            r"\bno\s+me\s+da\s+dinero\b",

            # Muy importante
            r"\bme\s+retiene\s+todo\b",
            r"\bme\s+retiene\s+todo\s+lo\s+que\s+gano\b",
            r"\bse\s+queda\s+con\s+todo\s+lo\s+que\s+gano\b",

            # Impedir trabajar / estudiar
            r"\bno\s+me\s+deja\s+trabajar\b",
            r"\bno\s+me\s+deja\s+laburar\b",
            r"\bno\s+me\s+deja\s+estudiar\b",
            r"\bno\s+me\s+deja\s+trabajar\b",
            r"\bno\s+me\s+deja\s+laburar\b",
            r"\bno\s+me\s+deja\s+tener\s+trabajo\b",
            r"\bno\s+me\s+deja\s+estudiar\b",
            # Manejo del dinero
            r"\bme\s+quit[oó]\s+todo\s+el\s+dinero\b",
            r"\bme\s+sac[oó]\s+todo\s+el\s+dinero\b",
            r"\bme\s+dej[oó]\s+sin\s+dinero\b",
            r"\bme\s+dej[oó]\s+sin\s+plata\b",
            r"\bse\s+qued[oó]\s+con\s+todo\s+mi\s+dinero\b",
            r"\bse\s+qued[oó]\s+con\s+todo\s+mi\s+sueldo\b",
            r"\bme\s+quit[oó]\s+todo\s+mi\s+sueldo\b",
            r"\bme\s+sac[oó]\s+todo\s+mi\s+sueldo\b",
            r"\bmaneja\s+mi\s+(plata|dinero|sueldo|cuenta|tarjeta)\b",
            r"\bcontrola\s+mi\s+(plata|dinero|sueldo|cuenta|tarjeta)\b",
            r"\bcontrola\s+cu[aá]nto\s+gasto\b",
            r"\bcontrola\s+mis\s+gastos\b",
            # Retener pensiones o ayudas
            r"\bme\s+quita\s+la\s+pensi[oó]n\b",
            r"\bse\s+queda\s+con\s+mi\s+pensi[oó]n\b",
            r"\bno\s+me\s+da\s+mi\s+pensi[oó]n\b",
            r"\bno\s+me\s+deja\s+usar\s+mi\s+pensi[oó]n\b",
            # Se queda con el sueldo / dinero
            r"\bse\s+queda\s+con\s+mi\s+(sueldo|plata|dinero)\b",
            r"\bse\s+qued[oó]\s+con\s+mi\s+(sueldo|plata|dinero)\b",
            # DETECCIONES ECONÓMICAS ADICIONALES (PARCHE NUEVO)
            r"\bmaneja\s+tod[ao]\s+mi\s+(dinero|plata|sueldo)\b",
            r"\bcontrola\s+tod[ao]\s+mi\s+(plata|dinero|sueldo)\b",
            r"\bcontrola\s+mi\s+(dinero|plata|sueldo)\b",
            r"\bcontrola\s+mi\s+dinero\b",
            r"\bcontrola\s+mi\s+plata\b",
            r"\bcontrola\s+mi\s+sueldo\b",
            r"\bme\s+retiene\s+el\s+sueldo\b",
            r"\bme\s+retiene\s+la\s+plata\b",
            r"\bme\s+retiene\s+el\s+dinero\b",
            r"\bme\s+controla\s+la\s+plata\b",
            r"\bme\s+controla\s+el\s+dinero\b",
            r"\bme\s+controla\s+el\s+sueldo\b",
            r"\bno\s+puedo\s+usar\s+mi\s+plata\b",
            r"\bno\s+puedo\s+usar\s+mi\s+dinero\b",
            r"\bno\s+puedo\s+usar\s+mi\s+sueldo\b",

            # Me quita o saca la plata / dinero
            r"\bme\s+quita\s+la\s+plata\b",
            r"\bme\s+saca\s+la\s+plata\b",
            r"\bme\s+roba\s+mi\s+dinero\b",
            r"\bme\s+quita\s+el\s+dinero\b",
            r"\bme\s+saca\s+el\s+dinero\b",
            r"\bme\s+quita\s+el\s+sueldo\b",
            # Versión sin "me": saca/quita el dinero
            r"\bsaca\s+el\s+dinero\b",
            r"\bquita\s+el\s+dinero\b",
            r"\bsaca\s+la\s+plata\b",
            r"\bse\s+queda\s+con\s+todo\s+mi\s+sueldo\b",

            # Tarjeta / documentos
            r"\bme\s+(saca|sac[óo]|sacar[aá]|va\s+a\s+sacar)\s+(mi\s+|la\s+)?tarjeta\b",
            r"\bme\s+quita\s+la\s+tarjeta\b",
            r"\bretiene\s+mis\s+documentos\b",
            r"\bretiene\s+mi\s+tarjeta\b",        
            r"\bme\s+retiene\s+la\s+tarjeta\b",
            r"\bme\s+quita\s+la\s+tarjeta\b",
            r"\bme\s+saca\s+la\s+tarjeta\b",
            r"\bme\s+roba\s+la\s+tarjeta\b",
            r"\bno\s+me\s+da\s+mi\s+tarjeta\b",

            # No me da plata / comida
            r"\bno\s+me\s+da\s+plata\b",
            r"\bno\s+me\s+da\s+dinero\b",
            r"\bno\s+me\s+da\s+plata\s+para\s+la\s+comida\b",
            r"\bno\s+me\s+da\s+para\s+la\s+comida\b",
            r"\bno\s+me\s+da\s+un\s+peso\b",
            r"\bme\s+deja\s+sin\s+plata\s+para\s+la\s+comida\b",

            # Retener plata
            r"\bme\s+retiene\s+la\s+plata\b",
            r"\bretiene\s+mi\s+plata\b",

            # Usa la tarjeta / sueldo sin permiso
            r"\bcontrola\s+mi\s+sueldo\b",
            r"\bme\s+usa\s+la\s+tarjeta\s+sin\s+permiso\b",
            r"\busa\s+mi\s+tarjeta\s+sin\s+que\s+yo\s+quiera\b",
            # Retener pensiones o ayudas
            r"\bme\s+quita\s+la\s+pensi[oó]n\b",
            r"\bse\s+queda\s+con\s+mi\s+pensi[oó]n\b",
            r"\bno\s+me\s+da\s+mi\s+pensi[oó]n\b",
            r"\bno\s+me\s+deja\s+usar\s+mi\s+pensi[oó]n\b",
            # Chantaje con plata
            r"\bme\s+chantajea\s+con\s+dinero\b",
            r"\bme\s+chantajea\s+con\s+plata\b",
            # Deudas, préstamos y control financiero
            r"\bme\s+deja\s+con\s+deudas\b",
            r"\bhace\s+deudas\s+a\s+mi\s+nombre\b",
            r"\bpid[ií]o\s+un\s+pr[eé]stamo\s+a\s+mi\s+nombre\b",
            r"\busa\s+mi\s+dinero\s+sin\s+mi\s+permiso\b",
            # Usar el dinero en vicios dejando sin recursos
            r"\bgasta\s+todo\s+en\s+alcohol\b",
            r"\bgasta\s+todo\s+en\s+drogas\b",
            r"\bgasta\s+todo\s+en\s+apuestas\b",
            r"\bse\s+gasta\s+todo\s+en\s+el\s+casino\b",

            # NUEVOS PATRONES AGREGADOS
            r"\bme\s+quit[óo]\s+(el\s+)?(dinero|plata|sueldo)\b",
            r"\bse\s+qued[óo]\s+con\s+(el\s+)?(dinero|plata|sueldo)\b",
            r"\bme\s+revisa\s+(los\s+)?(gastos|compras|recibos)\b",
            r"\bno\s+puedo\s+comprar\s+nada\b",
            r"\bme\s+pide\s+cuentas\s+de\s+(todo|cada)\b",
            r"\btiene\s+todo\s+a\s+su\s+nombre\b",
            r"\bme\s+oblig[óo]\s+a\s+dejar\s+(el\s+)?trabajo\b",
        ],

        "simbólica": [


            r"\bhace\s+chistes\s+machistas\b",
            r"\bsiempre\s+mensajes\s+machistas\b",
            r"\bse\s+burla\s+de\s+las\s+mujeres\b",
            r"\bme\s+cosifica\b",
            r"\bme\s+trata\s+como\s+un\s+objeto\b",
            r"\bdice\s+que\s+las\s+mujeres\s+son\s+todas\s+iguales\b",
            r"\bdice\s+que\s+las\s+mujeres\s+somos\s+inferiores\b",
        ],

        "institucional": [
       

            r"\bno\s+quisieron\s+tomar\s+mi\s+denuncia\b",
            r"\bno\s+me\s+quisieron\s+tomar\s+nada\b",
            r"\bme\s+dijeron\s+que\s+no\s+era\s+para\s+tanto\b",
            r"\bme\s+dijeron\s+que\s+vuelva\s+a\s+mi\s+casa\b",
            r"\bme\s+trataron\s+mal\s+cuando\s+fui\s+a\s+pedir\s+ayuda\b",
            r"\bse\s+burlaron\s+de\s+mi\s+situaci[oó]n\b",
            r"\bme\s+culparon\s+por\s+lo\s+que\s+pas[oó]\b",
            r"\bme\s+dijeron\s+que\s+yo\s+lo\s+provoqu[ée]\b",
            r"\bno\s+me\s+explicaron\s+c[oó]mo\s+seguir\b",
            r"\bme\s+hacen\s+repetir\s+mi\s+historia\b",
            r"\bperdieron\s+mi\s+denuncia\b",
            r"\bperdieron\s+el\s+expediente\b",
        ],
    }

    def name(self) -> Text:
        return "action_clasificar_violencia_mixta"

    @staticmethod
    def _normalizar_texto(texto: Text) -> Text:
        if not texto:
            return ""
        texto = texto.strip().lower()
        texto = re.sub(r"\s+", " ", texto)
        return texto

    def _detectar_tipos(self, texto: Text) -> List[Text]:
        """
        Devuelve una lista de tipos de violencia detectados en el texto.
        Puede contener varios tipos a la vez.
        """
        encontrados: List[Text] = []
        for tipo in self.ORDEN_TIPOS:
            patrones = self.TIPOS_VIOLENCIA.get(tipo, [])
            for patron in patrones:
                if re.search(patron, texto, flags=re.IGNORECASE):
                    encontrados.append(tipo)
                    break
        return encontrados

    @staticmethod
    def _formatear_lista_natural(items: List[Text]) -> Text:
        """
        ["A"] -> "A"
        ["A", "B"] -> "A y B"
        ["A", "B", "C"] -> "A, B y C"
        """
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        if len(items) == 2:
            return f"{items[0]} y {items[1]}"
        return f"{', '.join(items[:-1])} y {items[-1]}"

    def _construir_mensaje(self, tipos: List[Text]) -> Text:
        tipos_legibles = [self.NOMBRES_TIPOS[t] for t in tipos]
        lista_tipos = self._formatear_lista_natural(tipos_legibles)

        partes: List[Text] = []

        # Intro genérica
        partes.append(
            f"Por lo que me contás, veo señales de {lista_tipos}. "
            "Es muy duro vivir algo así, y quiero que sepas que **no es tu culpa**. 💜"
        )

        # Detalles por tipo
        if "física" in tipos:
            partes.append(
                "La violencia física nunca es justificable, aunque sea 'solo un empujón' "
                "o no te deje marcas visibles. Lo que te pasa es grave y merece ser tomado en serio."
            )

        if "psicológica" in tipos:
            partes.append(
                "La violencia psicológica puede ser muy desgastante: insultos, gritos, humillaciones, "
                "control del celular o las redes, celos excesivos, aislamiento o hacerte sentir culpable "
                "o 'loca'. Todo eso también es violencia, aunque no deje marcas en el cuerpo."
            )

        if "sexual" in tipos:
            partes.append(
                "Lo que contás también se parece a violencia sexual. El consentimiento tiene que ser libre, "
                "sin presiones, chantajes ni miedo. Si te sentiste obligada, incómoda o asustada, lo que pasó "
                "no está bien."
            )

        if "económica" in tipos:
            partes.append(
                "Lo que contás también se parece a violencia económica o patrimonial: usar la plata para "
                "controlar lo que hacés, quedarse con tu sueldo, no dejarte trabajar o manejar tus propios "
                "recursos, retener tus documentos o tarjetas."
            )

        if "simbólica" in tipos:
            partes.append(
                "También aparecen signos de violencia simbólica: chistes machistas, estereotipos o mensajes "
                "que menosprecian a las mujeres y sostienen ideas de desigualdad."
            )

        if "institucional" in tipos:
            partes.append(
                "Lo que describís también puede ser violencia institucional: cuando en lugares donde deberías "
                "recibir ayuda minimizan lo que te pasa, no te creen, no te toman la denuncia o te desaniman "
                "a seguir adelante."
            )

        partes.append(
            "Si querés, puedo explicarte con más detalle cada tipo de violencia o contarte dónde y cómo "
            "pedir ayuda de manera segura según tu situación.\n"
            "¿Te gustaría que hablemos de los tipos de violencia o preferís que veamos directamente recursos "
            "y lugares donde podés pedir ayuda?"
        )

        return "\n".join(partes)

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        ultimo_mensaje = tracker.latest_message.get("text", "")
        texto = self._normalizar_texto(ultimo_mensaje)

        if not texto:
            dispatcher.utter_message(
                "Gracias por escribirme. Me gustaría entender un poco más, ¿podés contarme con tus palabras qué está pasando?"
            )
            return []

        tipos_detectados = self._detectar_tipos(texto)

        if not tipos_detectados:
            dispatcher.utter_message(
                "Gracias por confiar en mí y contarme lo que estás viviendo. Aunque no pueda identificar con claridad "
                "un tipo de violencia solo por este mensaje, lo que sentís es muy importante y **no es tu culpa**. 💜\n\n"
                "Si querés, podés contarme un poco más con ejemplos concretos (qué hace, qué dice, cada cuánto pasa), "
                "o también puedo explicarte los distintos tipos de violencia para que veamos juntas si algo de eso te resuena.\n"
                "¿Te gustaría que hablemos de los tipos de violencia o preferís que veamos directamente recursos y lugares donde podés pedir ayuda?"
            )
            return [SlotSet("tipos_detectados", []), SlotSet("situacion_relatada", True)]

        tipos_ordenados = [t for t in self.ORDEN_TIPOS if t in tipos_detectados]

        mensaje = self._construir_mensaje(tipos_ordenados)
        dispatcher.utter_message(mensaje)

        return [
            SlotSet("tipos_detectados", tipos_ordenados),
            SlotSet("situacion_relatada", True),
        ]