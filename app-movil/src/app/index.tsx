import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { io } from 'socket.io-client';

const SERVIDOR_PYTHON_URL = 'http://10.236.129.191:5000';

const INVENTARIO_BASE = [
  { id: 'person', nombre: 'Persona (Operario)' },
  { id: 'cell phone', nombre: 'Celular' },
  { id: 'bottle', nombre: 'Botella' },
  { id: 'laptop', nombre: 'Computadora' },
  { id: 'scissors', nombre: 'Tijera (Simulando Pinza)' }
];

export default function Index() {
  const [objetosDetectados, setObjetosDetectados] = useState<string[]>([]);

  useEffect(() => {
    const socket = io(SERVIDOR_PYTHON_URL);

    socket.on('actualizacion_ia', (data) => {
      setObjetosDetectados(data.objetos);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <View style={styles.container}>
      
      <View style={styles.cabeceraPanel}>
        <Text style={styles.tituloLista}>INVENTARIO TABLERO A</Text>
        <Text style={styles.subtituloLista}>Verificación en tiempo real</Text>
      </View>

      <ScrollView style={styles.listaScroll}>
        {INVENTARIO_BASE.map((item) => {
          const estaPresente = objetosDetectados.includes(item.id);

          return (
            <View key={item.id} style={styles.itemObjeto}>
              
              <View style={styles.infoIzquierda}>
                <Ionicons 
                  name={estaPresente ? "checkmark-circle" : "close-circle"} 
                  size={32} 
                  color={estaPresente ? "#28a745" : "#dc3545"} 
                />
                <Text style={[
                  styles.textoObjeto, 
                  { color: estaPresente ? "#333" : "#888" }
                ]}>
                  {item.nombre}
                </Text>
              </View>
              
              <View style={[
                styles.switchStatus, 
                { backgroundColor: estaPresente ? "#28a745" : "#dc3545" }
              ]}>
                <Text style={styles.textoSwitch}>
                  {estaPresente ? "DETECTADO" : "FALTA"}
                </Text>
              </View>

            </View>
          );
        })}
      </ScrollView>

    </View>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1, 
    backgroundColor: '#ffffff', // Fondo completamente blanco
    padding: 20, 
    paddingTop: 60 
  },
  cabeceraPanel: {
    alignItems: 'center',
    marginBottom: 25,
    borderBottomWidth: 2,
    borderBottomColor: '#f0f0f0',
    paddingBottom: 15,
  },
  tituloLista: { color: '#0056b3', fontSize: 24, fontWeight: '900', letterSpacing: 1 },
  subtituloLista: { color: '#666', fontSize: 14, textTransform: 'uppercase', marginTop: 5 },
  listaScroll: { width: '100%' },
  
  itemObjeto: {
    flexDirection: 'row',
    justifyContent: 'space-between', 
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    paddingVertical: 18,
    paddingHorizontal: 15,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e9ecef',
    elevation: 3, // Sombra ligera en Android
    shadowColor: '#000', // Sombra ligera en iOS
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  infoIzquierda: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  textoObjeto: {
    fontSize: 18,
    fontWeight: 'bold',
    marginLeft: 15,
  },
  switchStatus: {
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  textoSwitch: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  }
});